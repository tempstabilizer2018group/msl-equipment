

import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

import msl.equipment.resources.picotech.picoscope
import msl.equipment

from msl.equipment.resources.picotech.picoscope import callbacks

# from msl.examples.equipment.resources.picotech.picoscope import record  # import the PicoScope EquipmentRecord

if __name__ == '__main__':

    print('Example :: Streaming Mode')

    record = msl.equipment.EquipmentRecord(
        manufacturer='Pico Technology',
        model='5442D',
        # serial='GQ903/0003',
        # resolution : :class:`str`, optional
        # The ADC resolution: 8, 12, 14, 15 or 16Bit. Only used by the PS5000A Series 
        # and it is ignored for all other PicoScope Series.
        # ps5000a.PS5000A_DEVICE_RESOLUTION = make_enum([
        #     "PS5000A_DR_8BIT",
        #     "PS5000A_DR_12BIT",
        #     "PS5000A_DR_14BIT",
        #     "PS5000A_DR_15BIT",
        #     "PS5000A_DR_16BIT",
        # ])
        connection=msl.equipment.ConnectionRecord(
            backend=msl.equipment.Backend.MSL,
            address='SDK::ps5000a',
            # properties={'open_async': True},  # opening in async mode is done in the properties
            properties=dict(
                resolution='16bit',
            )
        )
    )

    if False:
        # Working
        streaming_done = False

        @callbacks.ps5000aStreamingReady
        def my_streaming_ready(handle, num_samples, start_index, overflow, trigger_at, triggered, auto_stop, p_parameter):
            print('StreamingReady Callback: handle={}, num_samples={}, start_index={}, overflow={}, trigger_at={}, '
                'triggered={}, auto_stop={}, p_parameter={}'.format(handle, num_samples, start_index, overflow,
                                                                    trigger_at, triggered, auto_stop, p_parameter))
            # def get_values(self, num_samples=None, start_index=0, factor=1, ratio_mode='None', segment_index=0):
            # def get_values_bulk(self, from_segment_index=0, to_segment_index=None, factor=1, ratio_mode='None'):

            # scope.get_values(num_samples, start_index, factor=1, ratio_mode='None', segment_index=0)

            global streaming_done
            streaming_done = bool(auto_stop)

        scope = record.connect()  # establish a connection to the PicoScope
        scope.set_channel('A', scale='10V')  # enable Channel A and set the voltage range to be +/-10V
        scope.set_timebase(1e-3, 5)  # sample the voltage on Channel A every 1 ms, for 5 s
        scope.set_trigger('A', 0.0)  # Channel A is the trigger source with a trigger threshold value of 0.0 V
        scope.set_data_buffer('A')  # set the data buffer for Channel A
        scope.run_streaming()  # start streaming mode
        print('current_power_source: ' + scope.current_power_source())
        while not streaming_done:
            scope.wait_until_ready()  # wait until the latest streaming values are ready
            scope.get_streaming_latest_values(my_streaming_ready)  # get the latest streaming values
        print('Stopping the PicoScope')
        scope.stop()  # stop the oscilloscope from sampling data

    if True:
        streaming_done = False

        @callbacks.ps5000aStreamingReady
        def my_streaming_ready(handle, num_samples, start_index, overflow, trigger_at, triggered, auto_stop, p_parameter):
            print('StreamingReady Callback: handle={}, num_samples={}, start_index={}, overflow={}, trigger_at={}, '
                'triggered={}, auto_stop={}, p_parameter={}'.format(handle, num_samples, start_index, overflow,
                                                                    trigger_at, triggered, auto_stop, p_parameter))
            # def get_values(self, num_samples=None, start_index=0, factor=1, ratio_mode='None', segment_index=0):
            # def get_values_bulk(self, from_segment_index=0, to_segment_index=None, factor=1, ratio_mode='None'):

            # scope.get_values(num_samples, start_index, factor=1, ratio_mode='None', segment_index=0)

            global streaming_done
            streaming_done = bool(auto_stop)

        scope = record.connect()  # establish a connection to the PicoScope
        scope.set_channel('A', scale='10V')  # enable Channel A and set the voltage range to be +/-10V
        scope.set_timebase(1e-5, 2.0)  # sample the voltage on Channel A every 1 ms, for 5 s
        scope.set_trigger('A', 0.0)  # Channel A is the trigger source with a trigger threshold value of 0.0 V

        buffer = scope.channel['A'].buffer
        _buffer_size = buffer.size
        scope.set_data_buffer('A', buffer=buffer)  # set the data buffer for Channel A
        scope.run_streaming(auto_stop=False)  # start streaming mode
        print('current_power_source: ' + scope.current_power_source())
        while not streaming_done:
            scope.wait_until_ready()  # wait until the latest streaming values are ready
            scope.get_streaming_latest_values(my_streaming_ready)  # get the latest streaming values
        print('Stopping the PicoScope')
        scope.stop()  # stop the oscilloscope from sam

    if True:
        scope = record.connect()  # establish a connection to the PicoScope
