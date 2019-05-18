

import time
import logging
import matplotlib.pyplot as plt

logger = logging.getLogger(__name__)

logger.setLevel(logging.DEBUG)

import msl.equipment.resources.picotech.picoscope
import msl.equipment

from msl.equipment.resources.picotech.picoscope import callbacks

if __name__ == '__main__':

    print('Example :: Streaming Mode')

    record = msl.equipment.EquipmentRecord(
        manufacturer='Pico Technology',
        model='5442D',
        # serial='GQ903/0003',
        connection=msl.equipment.ConnectionRecord(
            backend=msl.equipment.Backend.MSL,
            address='SDK::ps5000a',
            # properties={'open_async': True},  # opening in async mode is done in the properties
            properties=dict(
                # resolution='14bit',  # only used for ps5000a series PicoScope's
                resolution='16bit',  # only used for ps5000a series PicoScope's
                auto_select_power= True,  # for PicoScopes that can be powered by an AC adaptor or by a USB cable
            )
        )
    )

    streaming_done = False
    g_samples = 0
    g_samples_last = 0
    g_triggered = 0
    g_trigger_at = 0
    g_start_index = 0
    g_start_index = 0

    @callbacks.ps5000aStreamingReady
    def my_streaming_ready(handle, num_samples, start_index, overflow, trigger_at, triggered, auto_stop, p_parameter):
        if False:
            print('StreamingReady Callback: handle={}, num_samples={}, start_index={}, overflow={}, trigger_at={}, '
                'triggered={}, auto_stop={}, p_parameter={}'.format(handle, num_samples, start_index, overflow,
                                                                trigger_at, triggered, auto_stop, p_parameter))
        if overflow:
            print('\noverflow')
        if triggered:
            print('\nTrigger')

        global g_samples
        global g_samples_last
        global g_triggered
        global g_trigger_at
        global g_num_samples
        global g_start_index

        g_samples += num_samples
        if g_samples > g_samples_last + sample_rate:
            # Every second one dot
            g_samples_last += sample_rate
            print('.', end='')

        g_triggered= triggered
        g_trigger_at = trigger_at
        g_num_samples= num_samples
        g_start_index = start_index

        global streaming_done
        streaming_done = bool(auto_stop)

    scope = record.connect()  # establish a connection to the PicoScope
    scope.set_channel('A', scale='10V')  # enable Channel A and set the voltage range to be +/-10V
    # scope.set_timebase(1e-4, 2.0)  # sample the voltage on Channel A every 1 ms, for 5 s
    max_sample_rate = 62.5e6
    sample_rate = max_sample_rate
    dt_s = 1.0/sample_rate
    buffer_size = 10e6
    sample_time_s = dt_s*buffer_size
    # dt, num_samples = scope.set_timebase(1e-6, 2.0)  # sample the voltage on Channel A every 1 us, for 100 us
    dt, num_samples = scope.set_timebase(dt_s, sample_time_s)  # sample the voltage on Channel A every 1 us, for 100 us
    scope.set_sig_gen_builtin_v2(start_frequency=1e6, pk_to_pk=2.0, offset_voltage=0.4)  # create a sine wave
    # scope.set_trigger('A', 1.0, timeout=-0e5)  # use Channel A as the trigger source at 1V, wait forever for a trigger event
    scope.set_trigger('A', 1.0, timeout=-0.01, direction='falling')  # use Channel A as the trigger source at 1V, wait forever for a trigger event

    scope.set_data_buffer('A')  # set the data buffer for Channel A
    scope.run_streaming(auto_stop=False)  # start streaming mode
    print('current_power_source: ' + scope.current_power_source())
    time_next_plot_s = time.time() + 5.0
    while not streaming_done:
        scope.wait_until_ready()  # wait until the latest streaming values are ready
        scope.get_streaming_latest_values(my_streaming_ready)  # get the latest streaming values
        if True:
            if time_next_plot_s > time.time():
                time_next_plot_s += 5.0
                idx_start = g_start_index
                idx_end = idx_start+200
                if idx_end > len(scope.channel['A'].buffer):
                    continue
                # idx_end = g_start_index+g_num_samples
                plt.plot(list(range(idx_start, idx_end)), scope.channel['A'].buffer[idx_start:idx_end])
                filename = __file__.replace('.py', '_{:12.1f}.png'.format(time_next_plot_s))
                plt.savefig(fname=filename)
                plt.clf()

        if True:
            if g_triggered > 0:
                SPAN = 10
                start = g_start_index + g_trigger_at - SPAN//2
                start = max(0, start)
                end = start+SPAN
                list_values = scope.channel['A'].volts[start:end]
                for v in list_values:
                    print('{:0.5f} V'.format(v))
                if False:
                    for i in range(10):
                        index = g_start_index + i + g_trigger_at - 5
                        if index < 0:
                            continue
                    print('{} {} {:0.5f} V'.format(i, index, scope.channel['A'].volts[index]))

    print('Stopping the PicoScope')
    scope.stop()  # stop the oscilloscope from sam
