"""
This example outputs a custom waveform and records the waveform on Channel A.

The output of the AWG must be connected to Channel A.
"""

import msl.equipment.resources.picotech.picoscope
import msl.equipment

# this "if" statement is used so that Sphinx does not execute this script when the docs are being built
if __name__ == '__main__':
    import numpy as np

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

    print('Example :: Acquire AWG custom waveform')

    scope = record.connect()  # establish a connection to the PicoScope
    scope.set_channel('A', scale='2V')  # enable Channel A and set the voltage range to be +/-2V
    dt, num_samples = scope.set_timebase(10e-3, 5.0)  # sample the voltage on Channel A every 10 ms for 5 s
    scope.set_trigger('A', -0.2, timeout=5.0, direction='falling')  # use Channel A as the trigger source

    # simulate the Lennard-Jones Potential
    x = np.linspace(0.88, 2, 500)
    awg = (1/x)**12 - 2*(1/x)**6
    scope.set_sig_gen_arbitrary(awg, repetition_rate=1e3, index_mode='quad', pk_to_pk=2.0)

    scope.run_block(pre_trigger=2.5)  # start acquisition
    scope.wait_until_ready()  # wait until all requested samples are collected
    scope.set_data_buffer('A')  # set the data buffer for Channel A
    scope.get_values()  # fill the data buffer of Channel A with the values saved in the PicoScope's internal memory
    scope.stop()  # stop the oscilloscope from sampling data

    print('Channel A input')
    t = np.arange(-scope.pre_trigger, dt*num_samples-scope.pre_trigger, dt)
    for i in range(num_samples):
        print('{0:f}, {1:f}'.format(t[i], scope.channel['A'].volts[i]))

    # if matplotlib is available then plot the results
    try:
        import matplotlib.pyplot as plt
    except ImportError:
        pass
    else:
        plt.plot(t, scope.channel['A'].volts, 'bo')
        plt.show()
