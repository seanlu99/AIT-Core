from ait.server.plugin import Plugin
from ait.core import limits, logs, tlm

class TelemetryMonitorPlugin(Plugin):
    def __init__(self, name, **kwargs):
        super(ExamplePlugin, self).__init__(name, **kwargs)

        limit_dict = defaultdict(dict)
        for k, v in limits.getDefaultDict().iteritems():
            packet, field = k.split('.')
            limit_dict[packet][field] = v

        packet_dict = tlm.getDefaultDict()

        notif_thrshld = ait.config.get('notifications.options.threshold', 1)
        notif_freq = ait.config.get('notifications.options.frequency', float('inf'))

        log.info('Starting telemetry limit monitoring')

    def process(self, input_data, topic=None):
        if input_data._defn.name not in limit_dict: return

        for field, defn in limit_dict[input_data.name].iteritems():
            v = decoded._getattr(field)

            if input_data.name not in limit_trip_repeats.keys():
                limit_trip_repeats[input_data.name] = {}

            if field not in limit_trip_repeats[input_data.name].keys():
                limit_trip_repeats[input_data.name][field] = 0

            if defn.error(v):
                msg = 'Field {} error out of limit with value {}'.format(field, v)
                log.error(msg)

                limit_trip_repeats[input_data.name][field] += 1
                repeats = limit_trip_repeats[input_data.name][field]

                if (repeats == notif_thrshld or
                    (repeats > notif_thrshld and
                    (repeats - notif_thrshld) % notif_freq == 0)):
                    notify.trigger_notification('limit-error', msg)

            elif defn.warn(v):
                msg = 'Field {} warning out of limit with value {}'.format(field, v)
                log.warn(msg)

                limit_trip_repeats[input_data.name][field] += 1
                repeats = limit_trip_repeats[input_data.name][field]

                if (repeats == notif_thrshld or
                    (repeats > notif_thrshld and
                    (repeats - notif_thrshld) % notif_freq == 0)):
                    notify.trigger_notification('limit-warn', msg)

            else:
                limit_trip_repeats[input_data.name][field] = 0
