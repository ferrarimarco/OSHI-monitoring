import logging
import os
import config

_RX_BYTES_BUFFER = 'rx_bytes_buffer'
_RX_BYTES_BUFFER_INDEX = 'rx_bytes_buffer_index'
_TX_BYTES_BUFFER = 'tx_bytes_buffer'
_TX_BYTES_BUFFER_INDEX = 'tx_bytes_buffer_index'
_RX_PACKETS_BUFFER = 'rx_packets_buffer'
_RX_PACKETS_BUFFER_INDEX = 'rx_packets_buffer_index'
_TX_PACKETS_BUFFER = 'tx_packets_buffer'
_TX_PACKETS_BUFFER_INDEX = 'tx_packets_buffer_index'
_SDN_RX_BYTES_BUFFER = 'sdn_rx_bytes_buffer'
_SDN_RX_BYTES_BUFFER_INDEX = 'sdn_rx_bytes_buffer_index'
_SDN_TX_BYTES_BUFFER = 'sdn_tx_bytes_buffer'
_SDN_TX_BYTES_BUFFER_INDEX = 'sdn_tx_bytes_buffer_index'
_SDN_RX_PACKETS_BUFFER = 'sdn_rx_packets_buffer'
_SDN_RX_PACKETS_BUFFER_INDEX = 'sdn_rx_packets_buffer_index'
_SDN_TX_PACKETS_BUFFER = 'sdn_tx_packets_buffer'
_SDN_TX_PACKETS_BUFFER_INDEX = 'sdn_tx_packets_buffer_index'

RX_BYTES = 'rx_bytes'
TX_BYTES = 'tx_bytes'
RX_PACKETS = 'rx_packets'
TX_PACKETS = 'tx_packets'
SDN_RX_BYTES = 'sdn_rx_bytes'
SDN_TX_BYTES = 'sdn_tx_bytes'
SDN_RX_PACKETS = 'sdn_rx_packets'
SDN_TX_PACKETS = 'sdn_tx_packets'

PORT_STATS = {RX_BYTES, TX_BYTES,
              RX_PACKETS, TX_PACKETS,
              SDN_RX_BYTES, SDN_TX_BYTES,
              SDN_RX_PACKETS, SDN_TX_PACKETS}

IP_PARTNER_PORT_NUMBER = 'ip_partner_port_number'
PORT_NAME = 'name'

log = logging.getLogger('oshi.monitoring.switch_stat')
log.setLevel(logging.DEBUG)
# create file handler which logs even debug messages
fh = logging.FileHandler(os.path.join(config.RRD_LOG_PATH, "switch_stat.log"))
fh.setLevel(logging.DEBUG)
# create console handler with a higher log level
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
# create formatter and add it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
ch.setFormatter(formatter)
fh.setFormatter(formatter)
# add the handlers to logger
log.addHandler(ch)
log.addHandler(fh)
log.propagate = False


class SwitchStats:
    def __init__(self, datapath):
        self.data_path = datapath
        self.ports = {}
        self.__seconds_from_start = 0
        log.debug("Initializing SwitchStat for %s datapath", datapath.id)

    def add_port(self, port_number):
        """
        Add a single port to stats.

        :param port_number: port number of the port to add
        """
        self.ports[port_number] = {}
        self.ports[port_number][RX_BYTES] = 0
        self.ports[port_number][_RX_BYTES_BUFFER] = [0] * config.DELTA_WINDOW
        self.ports[port_number][_RX_BYTES_BUFFER_INDEX] = 0
        self.ports[port_number][TX_BYTES] = 0
        self.ports[port_number][_TX_BYTES_BUFFER] = [0] * config.DELTA_WINDOW
        self.ports[port_number][_TX_BYTES_BUFFER_INDEX] = 0
        self.ports[port_number][RX_PACKETS] = 0
        self.ports[port_number][_RX_PACKETS_BUFFER] = [0] * config.DELTA_WINDOW
        self.ports[port_number][_RX_PACKETS_BUFFER_INDEX] = 0
        self.ports[port_number][TX_PACKETS] = 0
        self.ports[port_number][_TX_PACKETS_BUFFER] = [0] * config.DELTA_WINDOW
        self.ports[port_number][_TX_PACKETS_BUFFER_INDEX] = 0
        # SDN BUFFERS
        self.ports[port_number][_SDN_RX_BYTES_BUFFER] = [0] * config.DELTA_WINDOW
        self.ports[port_number][_SDN_RX_BYTES_BUFFER_INDEX] = 0
        self.ports[port_number][_SDN_TX_BYTES_BUFFER] = [0] * config.DELTA_WINDOW
        self.ports[port_number][_SDN_TX_BYTES_BUFFER_INDEX] = 0
        self.ports[port_number][_SDN_RX_PACKETS_BUFFER] = [0] * config.DELTA_WINDOW
        self.ports[port_number][_SDN_RX_PACKETS_BUFFER_INDEX] = 0
        self.ports[port_number][_SDN_TX_PACKETS_BUFFER] = [0] * config.DELTA_WINDOW
        self.ports[port_number][_SDN_TX_PACKETS_BUFFER_INDEX] = 0

    def delete_port(self, port_number):
        """
        Remove specified port from stats.

        :param port_number: port number of the port to remove
        """
        del self.ports[port_number]

    def get_port(self, port_number):
        """
        Return the specified port.

        :param port_number:
        :return: the specified port
        """
        return self.ports[port_number]

    def set_port_name(self, port_number, port_name):
        """
        Set name for the specified port.

        :param port_number
        :param port_name: name to set
        """
        self.ports[port_number][PORT_NAME] = port_name

    def get_port_name(self, port_number):
        """
        Return the name of the specified port.

        :param port_number:
        :return: port name
        """
        return self.ports[port_number][PORT_NAME]

    def get_datapath(self):
        """
        Return the datapath of the SwitchStats object.

        :return: datapath
        """
        return self.data_path

    def set_ip_partner_port_number(self, port_number, partner_port_number):
        """
        Set the port number of the IP partner for a given port.

        This can be used to match ports between partners like:
            ss.set_ip_partner_port_number(in_port, out_port)
            ss.set_ip_partner_port_number(out_port, in_port)

        :param port_number:
        :param partner_port_number:
        """
        self.ports[port_number][IP_PARTNER_PORT_NUMBER] = partner_port_number

    def get_ip_partner_port_number(self, port_number):
        """
        Return the port number of the IP partner, given a port number.

        :param port_number:
        :return: Partner port number or -1 if no relationship has been defined for the specified port number.
        """
        if IP_PARTNER_PORT_NUMBER in self.ports[port_number]:
            return self.ports[port_number][IP_PARTNER_PORT_NUMBER]
        else:
            raise KeyError('IP partner not found for port ' + port_number)

    def get_rx_bytes(self, port_number):
        """
        Return received bytes count for the specified port.

        :param port_number:
        :return: bytes count
        """
        return self.ports[port_number][RX_BYTES]

    def get_tx_bytes(self, port_number):
        """
        Return transmitted bytes count for the specified port.

        :param port_number:
        :return: bytes count
        """
        return self.ports[port_number][TX_BYTES]

    def get_rx_packets(self, port_number):
        """
        Return received packet count for the specified port.

        :param port_number:
        :return: packet count
        """
        return self.ports[port_number][RX_PACKETS]

    def get_tx_packets(self, port_number):
        """
        Return transmitted packet count for the specified port.

        :param port_number:
        :return: packet count
        """
        return self.ports[port_number][TX_PACKETS]

    def _update_stat(self, port_number, buffer_index_key, buffer_key, stat_key, stat_value, lldp_noise=0):
        """
        Update stat value filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param stat_value:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        log.debug("Update %s stat for %s datapath, port %s with value: %s", stat_key, self.data_path.id, port_number,
                  stat_value)
        port = self.ports[port_number]
        log.debug("Current stats for port %s: %s", port_number, str(port))
        # Time interval definition
        time_interval_end = port[buffer_index_key]
        time_interval_start = (time_interval_end - 1) % config.DELTA_WINDOW
        log.debug("Time interval start for %s port: %s", port_number, time_interval_start)
        log.debug("Time interval end for %s port: %s", port_number, time_interval_end)
        # stat count recorded @ time_interval_start
        time_interval_start_count = port[buffer_key][time_interval_start]
        log.debug("%s (buffer_key: %s) count @ time_interval_start for port %s: %s", stat_key, buffer_key, port_number,
                  time_interval_start_count)

        # update stat if necessary (time_interval_start_count == 0 if the buffer is partially empty)
        if time_interval_start_count != 0:
            updated_value = stat_value - time_interval_start_count - lldp_noise
            log.debug("Updating %s for port %s with value: %s", stat_key, port_number, updated_value)
            self.ports[port_number][stat_key] += updated_value
        else:
            log.debug("Update for %s not yet necessary for port %s as the buffer is not yet full", stat_key,
                      port_number)
        log.debug("Current stats for port %s (after update check): %s", port_number, str(port))

        # update time interval start
        time_interval_start_updated_value = (port[buffer_index_key] + 1) % config.DELTA_WINDOW
        log.debug("Update time_interval_start for %s buffer, port %s with value: %s", buffer_index_key, port_number,
                  time_interval_start_updated_value)
        port[buffer_index_key] = time_interval_start_updated_value

        # update stat count received @ time_interval_end
        port[buffer_key][time_interval_end] = stat_value
        log.debug("Update time_interval_end for %s buffer, port %s with value: %s", buffer_key, port_number,
                  stat_value)
        log.debug("Current stats for port %s after all the updates: %s", port_number, str(port))

    def set_rx_bytes(self, port_number, rx_bytes, lldp_noise=0):
        """
        Update received byte count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param rx_bytes:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, _RX_BYTES_BUFFER_INDEX, _RX_BYTES_BUFFER, RX_BYTES, rx_bytes, lldp_noise)

    def set_tx_bytes(self, port_number, tx_bytes, lldp_noise=0):
        """
        Update transmitted byte count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param tx_bytes:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, _TX_BYTES_BUFFER_INDEX, _TX_BYTES_BUFFER, TX_BYTES, tx_bytes, lldp_noise)

    def set_rx_packets(self, port_number, rx_packets, lldp_noise=0):
        """
        Update received packet count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param rx_packets:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, _RX_PACKETS_BUFFER_INDEX, _RX_PACKETS_BUFFER, RX_PACKETS, rx_packets,
                          lldp_noise)

    def set_tx_packets(self, port_number, tx_packets, lldp_noise=0):
        """
        Update transmitted packet count filling a circular buffer of config.DELTA_WINDOW for the specified port.

        :param port_number:
        :param tx_packets:
        :param lldp_noise: LLDP traffic to subtract to rx_bytes, defaults to 0
        :return:
        """
        self._update_stat(port_number, _TX_PACKETS_BUFFER_INDEX, _TX_PACKETS_BUFFER, TX_PACKETS, tx_packets,
                          lldp_noise)

    def _get_sdn_stat(self, port_number, stat_index_key, stat_key):
        port = self.ports[port_number]
        index = (port[stat_index_key] - 1) % config.DELTA_WINDOW
        return port[stat_key][index]

    def get_sdn_rx_bytes(self, port_number):
        """
        Return the received SDN traffic for the specified port.

        :param port_number:
        :return: SDN traffic expressed in bytes
        """
        return self._get_sdn_stat(port_number, _SDN_RX_BYTES_BUFFER_INDEX, _SDN_RX_BYTES_BUFFER)

    def get_sdn_rx_packets(self, port_number):
        """
        Return the received SDN traffic for the specified port.

        :param port_number:
        :return: SDN traffic expressed in packets
        """
        return self._get_sdn_stat(port_number, _SDN_RX_PACKETS_BUFFER_INDEX, _SDN_RX_PACKETS_BUFFER)

    def get_sdn_tx_bytes(self, port_number):
        """
        Return the transmitted SDN traffic for the specified port.

        :param port_number:
        :return: SDN traffic expressed in bytes
        """
        return self._get_sdn_stat(port_number, _SDN_TX_BYTES_BUFFER_INDEX, _SDN_TX_BYTES_BUFFER)

    def get_sdn_tx_packets(self, port_number):
        """
        Return the transmitted SDN traffic for the specified port.

        :param port_number:
        :return: SDN traffic expressed in packets
        """
        return self._get_sdn_stat(port_number, _SDN_TX_PACKETS_BUFFER_INDEX, _SDN_TX_PACKETS_BUFFER)

    def __get_sdn_rx_bytes(self, port_number):
        """
        Compute and return received SDN traffic for the specified port.

        :param port_number:
        :return: Received SDN traffic in bytes
        """
        try:
            ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        except KeyError:
            return -1
        # received total - ip sent to partner
        return self.get_rx_bytes(port_number) - self.get_tx_bytes(ip_partner_port_number)

    def __get_sdn_rx_packets(self, port_number):
        """
        Compute and return received SDN traffic for the specified port.

        :param port_number:
        :return: Received SDN traffic in packets
        """
        try:
            ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        except KeyError:
            return -1
        # received total - ip sent to partner
        return self.get_rx_packets(port_number) - self.get_tx_packets(ip_partner_port_number)

    def __get_sdn_tx_bytes(self, port_number):
        """
        Compute and return transmitted SDN traffic for the specified port.

        :param port_number:
        :return: Transmitted SDN traffic in bytes
        """
        try:
            ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        except KeyError:
            return -1
        sdn_bytes = 0
        # sent total - ip received by partner
        sdn_bytes += self.get_tx_bytes(port_number) - self.get_rx_bytes(ip_partner_port_number)
        return sdn_bytes

    def __get_sdn_tx_packets(self, port_number):
        """
        Compute and return transmitted SDN traffic for the specified port.

        :param port_number:
        :return: Transmitted SDN traffic in packets
        """
        try:
            ip_partner_port_number = self.get_ip_partner_port_number(port_number)
        except KeyError:
            return -1
        sdn_packets = 0
        # sent total - ip received by partner
        sdn_packets += self.get_tx_packets(port_number) - self.get_rx_packets(ip_partner_port_number)
        return sdn_packets

    @staticmethod
    def _has_rx_lldp_noise(port_name, port_number):
        if port_name[0:3] == 'cro':
            return 0
        elif port_number != 1:
            return 1
        return 0

    def _update_sdn_stats(self):
        """
        Update SDN stats for every port registered in this SwitchStats

        :return:
        """
        self.__seconds_from_start += 1
        for port_number in self.ports:
            p = self.ports[port_number]
            rx_noise = SwitchStats._has_rx_lldp_noise(self.get_port_name(port_number), port_number)
            t1_sdn = p[_SDN_RX_BYTES_BUFFER_INDEX]
            p[_SDN_RX_BYTES_BUFFER_INDEX] = (p[_SDN_RX_BYTES_BUFFER_INDEX] + 1) % config.DELTA_WINDOW
            p[_SDN_RX_BYTES_BUFFER][t1_sdn] = self.__get_sdn_rx_bytes(port_number) + (
                self.__seconds_from_start * config.LLDP_NOISE_BYTE_S * rx_noise)
            t1_sdn = p[_SDN_TX_BYTES_BUFFER_INDEX]
            p[_SDN_TX_BYTES_BUFFER_INDEX] = (p[_SDN_TX_BYTES_BUFFER_INDEX] + 1) % config.DELTA_WINDOW
            p[_SDN_TX_BYTES_BUFFER][t1_sdn] = self.__get_sdn_tx_bytes(port_number) - (
                self.__seconds_from_start * config.LLDP_NOISE_BYTE_S)
            t1_sdn = p[_SDN_RX_PACKETS_BUFFER_INDEX]
            p[_SDN_RX_PACKETS_BUFFER_INDEX] = (p[_SDN_RX_PACKETS_BUFFER_INDEX] + 1) % config.DELTA_WINDOW
            p[_SDN_RX_PACKETS_BUFFER][t1_sdn] = self.__get_sdn_rx_packets(port_number) + (
                self.__seconds_from_start * config.LLDP_NOISE_PACK_S * rx_noise)
            t1_sdn = p[_SDN_TX_PACKETS_BUFFER_INDEX]
            p[_SDN_TX_PACKETS_BUFFER_INDEX] = (p[_SDN_TX_PACKETS_BUFFER_INDEX] + 1) % config.DELTA_WINDOW
            p[_SDN_TX_PACKETS_BUFFER][t1_sdn] = self.__get_sdn_tx_packets(port_number) - (
                self.__seconds_from_start * config.LLDP_NOISE_PACK_S)

    def get_current_values(self, port_number):
        self._update_sdn_stats()
        return {RX_BYTES: self.get_rx_bytes(port_number), TX_BYTES: self.get_tx_bytes(port_number),
                RX_PACKETS: self.get_rx_packets(port_number), TX_PACKETS: self.get_tx_packets(port_number),
                SDN_RX_BYTES: self.get_sdn_rx_bytes(port_number),
                SDN_TX_BYTES: self.get_sdn_tx_bytes(port_number),
                SDN_RX_PACKETS: self.get_sdn_rx_packets(port_number),
                SDN_TX_PACKETS: self.get_sdn_tx_bytes(port_number)}
