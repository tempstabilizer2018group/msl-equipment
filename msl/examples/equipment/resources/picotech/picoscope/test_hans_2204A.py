

import logging

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

import msl.equipment.resources.picotech.picoscope
import msl.equipment

from msl.equipment.resources.picotech.picoscope import callbacks

from msl.equipment.resources.picotech.picoscope import callbacks
# from msl.examples.equipment.resources.picotech.picoscope import record  # import the PicoScope EquipmentRecord

if __name__ == '__main__':

    print('Example :: Streaming Mode')
    record = msl.equipment.EquipmentRecord(
        manufacturer='Pico Technology',
        model='2204A',
        serial='FU818/554',
        connection=msl.equipment.ConnectionRecord(
            backend=msl.equipment.Backend.MSL,
            address='SDK::ps2000',
            properties={},  # opening in async mode is done in the properties
            # properties={'open_async': True},  # opening in async mode is done in the properties
        )
    )

    streaming_done = False

    @callbacks.GetOverviewBuffersMaxMin
    def my_get_overview_buffer(overviewBuffers, overflow, triggeredAt, triggered, auto_stop, nValues):
        print('StreamingReady Callback: overviewBuffers={}, overflow={}, auto_stop={}, nValues={}'.format(overviewBuffers, overflow, auto_stop, nValues))
        global streaming_done
        streaming_done = bool(auto_stop)

    scope = record.connect()  # establish a connection to the PicoScope
    scope.set_channel('A', scale='10V')  # enable Channel A and set the voltage range to be +/-10V
    # scope.set_timebase(1e-3, 5)  # sample the voltage on Channel A every 1 ms, for 5 s
    # scope.set_trigger('A', 0.0)  # Channel A is the trigger source with a trigger threshold value of 0.0 V
    # scope.set_data_buffer('A')  # set the data buffer for Channel A
    scope.run_streaming()  # start streaming mode
    while not streaming_done:
        scope.wait_until_ready()  # wait until the latest streaming values are ready
        scope.get_streaming_latst_value(my_get_overview_buffer)  # get the latest streaming values
    print('Stopping the PicoScope')
    scope.stop()  # stop the oscilloscope from sampling data
