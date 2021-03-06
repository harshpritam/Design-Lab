from pox.core import core
import pox.openflow.libopenflow_01 as of
from pox.lib.util import dpid_to_str, str_to_dpid
from pox.lib.util import str_to_bool
from pox.lib.addresses import IPAddr, IPAddr6, EthAddr
import time

log = core.getLogger()

# We don't want to flood immediately when a switch connects.
# Can be overriden on commandline.
_flood_delay = 0


class LearningSwitch (object):
  
  def __init__ (self, connection, transparent):
    # Switch we'll be adding L2 learning switch capabilities to
    self.connection = connection
    self.transparent = transparent

    # Our table
    self.macToPort = {}
    self.utilTable = {}
    self.exec_time = 0
    self.count_h1 = 0
    self.count_h2 = 0
    self.tot_count = 0

    # We want to hear PacketIn messages, so we listen
    # to the connection
    connection.addListeners(self)

    # We just use this to know when to log a helpful message
    self.hold_down_expired = _flood_delay == 0

    #log.debug("Initializing LearningSwitch, transparent=%s",
    #          str(self.transparent))
  
  def AddRule(self, dpidstr, src=0, value=False):
    self.utilTable[(dpidstr,src)] = value
    log.debug("Adding rule in %s: %s", dpidstr, src)
  
  def DeleteRule(self, dpidstr, src=0):
    try:
      del self.utilTable[(dpidstr,src)]
      log.debug("Deleting Rule in %s: %s", dpidstr, src)
    except KeyError:
      log.error("Cannot find in %s: %s", dpidstr, src)
  
  def CheckRule(self, dpidstr, src=0):
    try:
      entry = self.utilTable[(dpidstr,src)]
      if (entry == True):
        log.debug("Rule (%s) found in %s: FORWARD", src, dpidstr)
      else:
        log.debug("Rule (%s) found in %s: DROP", src, dpidstr)
      return entry
    except KeyError:
      log.debug("Rule (%s) NOT found in %s: FORWARD", src, dpidstr)
      return True

  def _handle_PacketIn (self, event):
    """
    Handle packet in messages from the switch to implement above algorithm.
    """
    start_time = time.time()
    packet = event.parsed

    def flood (message = None):
      """ Floods the packet """
      msg = of.ofp_packet_out()
      if time.time() - self.connection.connect_time >= _flood_delay:
        # Only flood if we've been connected for a little while...

        if self.hold_down_expired is False:
          # Oh yes it is!
          self.hold_down_expired = True
          log.info("%s: Flood hold-down expired -- flooding",
              dpid_to_str(event.dpid))

        if message is not None: log.debug(message)
        #log.debug("%i: flood %s -> %s", event.dpid,packet.src,packet.dst)
        # OFPP_FLOOD is optional; on some switches you may need to change
        # this to OFPP_ALL.
        msg.actions.append(of.ofp_action_output(port = of.OFPP_FLOOD))
      else:
        pass
        #log.info("Holding down flood for %s", dpid_to_str(event.dpid))
      msg.data = event.ofp
      msg.in_port = event.port
      self.connection.send(msg)

    def drop (duration = None):
      """
      Drops this packet and optionally installs a flow to continue
      dropping similar ones for a while
      """
      if duration is not None:
        if not isinstance(duration, tuple):
          duration = (duration,duration)
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet)
        msg.idle_timeout = duration[0]
        msg.hard_timeout = duration[1]
        msg.buffer_id = event.ofp.buffer_id
        self.connection.send(msg)
      elif event.ofp.buffer_id is not None:
        msg = of.ofp_packet_out()
        msg.buffer_id = event.ofp.buffer_id
        msg.in_port = event.port
        self.connection.send(msg)

    self.macToPort[packet.src] = event.port # 1
    dpidstr = dpid_to_str(event.connection.dpid)
    if packet.src == EthAddr("00:00:00:00:00:02"):
      dpidstr1 = dpidstr
      self.count_h1 = self.count_h1 + 1
    else:
      if packet.src == EthAddr("00:00:00:00:00:03"):
        dpidstr2 = dpidstr
        self.count_h2 = self.count_h2 + 1
    
    if (self.exec_time >= 1 and self.tot_count >= 1000):
      self.AddRule(dpidstr1, EthAddr("00:00:00:00:00:02"))
      self.count_h1 = 0
      self.count_h2 = 0
      self.exec_time = 0
    else:
      if (self.exec_time >= 1 and self.tot_count < 1000):
        self.DeleteRule(dpidstr1, EthAddr("00:00:00:00:00:02"))
        
    if self.CheckRule(dpidstr, packet.src) == False:
      drop()
      return

    if not self.transparent: # 2
      if packet.type == packet.LLDP_TYPE or packet.dst.isBridgeFiltered():
        drop() # 2a
        return

    if packet.dst.is_multicast:
      flood() # 3a
    else:
      if packet.dst not in self.macToPort: # 4
        flood("Port for %s unknown -- flooding" % (packet.dst,)) # 4a
      else:
        port = self.macToPort[packet.dst]
        if port == event.port: # 5
          # 5a
          log.warning("Same port for packet from %s -> %s on %s.%s.  Drop."
              % (packet.src, packet.dst, dpid_to_str(event.dpid), port))
          drop(10)
          return
        # 6
        log.debug("installing flow for %s.%i -> %s.%i" %
                  (packet.src, event.port, packet.dst, port))
        msg = of.ofp_flow_mod()
        msg.match = of.ofp_match.from_packet(packet, event.port)
        msg.idle_timeout = 10
        msg.hard_timeout = 30
        msg.actions.append(of.ofp_action_output(port = port))
        msg.data = event.ofp # 6a
        self.connection.send(msg)
    end_time = time.time()
    self.exec_time = self.exec_time + end_time - start_time  

class l2_learning (object):
  """
  Waits for OpenFlow switches to connect and makes them learning switches.
  """
  def __init__ (self, transparent, ignore = None):
    """
    Initialize

    See LearningSwitch for meaning of 'transparent'
    'ignore' is an optional list/set of DPIDs to ignore
    """
    core.openflow.addListeners(self)
    self.transparent = transparent
    self.ignore = set(ignore) if ignore else ()

  def _handle_ConnectionUp (self, event):
    if event.dpid in self.ignore:
      log.debug("Ignoring connection %s" % (event.connection,))
      return
    log.debug("Connection %s" % (event.connection,))
    LearningSwitch(event.connection, self.transparent)


def launch (transparent=False, hold_down=_flood_delay, ignore = None):
  """
  Starts an L2 learning switch.
  """
  try:
    global _flood_delay
    _flood_delay = int(str(hold_down), 10)
    assert _flood_delay >= 0
  except:
    raise RuntimeError("Expected hold-down to be a number")

  if ignore:
    ignore = ignore.replace(',', ' ').split()
    ignore = set(str_to_dpid(dpid) for dpid in ignore)

  core.registerNew(l2_learning, str_to_bool(transparent), ignore)