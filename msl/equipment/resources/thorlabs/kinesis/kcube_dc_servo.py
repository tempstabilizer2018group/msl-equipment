"""
This module provides all the functionality required to control a
KCube DC Servo (KDC101).
"""
from ctypes import c_int16, c_short, c_int, c_uint, c_int32, c_int64, c_double, byref

from msl.equipment.resources.utils import WORD, DWORD
from msl.equipment.resources.thorlabs.kinesis.motion_control import MotionControl
from msl.equipment.resources.thorlabs.kinesis.api_functions import KCube_DCServo_FCNS
from msl.equipment.resources.thorlabs.kinesis.structs import (
    TLI_HardwareInformation,
    MOT_VelocityParameters,
    MOT_HomingParameters,
    MOT_JogParameters,
    MOT_LimitSwitchParameters,
    MOT_DC_PIDParameters,
    KMOT_MMIParams,
    KMOT_TriggerConfig,
    KMOT_TriggerParams,
)
from msl.equipment.resources.thorlabs.kinesis.enums import (
    MOT_JogModes,
    MOT_StopModes,
    MOT_TravelDirection,
    MOT_LimitSwitchModes,
    MOT_LimitSwitchSWModes,
    MOT_LimitsSoftwareApproachPolicy,
    MOT_HomeLimitSwitchDirection,
    MOT_TravelModes,
    UnitType,
    KMOT_JoyStickMode,
    KMOT_JoystickDirectionSense,
    KMOT_TriggerPortMode,
    KMOT_TriggerPortPolarity,
)


class KCubeDCServo(MotionControl):

    def __init__(self, record):
        """A wrapper around ``Thorlabs.MotionControl.KCube.DCServo.dll``.

        The :obj:`~msl.equipment.record_types.ConnectionRecord.properties`
        for a KCubeDCServo connection supports the following key-value pairs in the
        :ref:`connection_database`::

            'load_settings': bool,  # optional, default is True (load the settings when the connection is created)

        Do not instantiate this class directly. Use the :meth:`~.EquipmentRecord.connect`
        method to connect to the equipment.

        Parameters
        ----------
        record : :class:`~msl.equipment.record_types.EquipmentRecord`
            A record from an :ref:`equipment_database`.
        """
        MotionControl.__init__(self, record, KCube_DCServo_FCNS)
        if record.connection.properties.get('load_settings', True):
            self.load_settings()

    def can_home(self):
        """Can the device perform a :meth:`home`?

        Returns
        -------
        :obj:`bool`
            Whether the device can be homed.
        """
        return self.sdk.CC_CanHome(self._serial)

    def can_move_without_homing_first(self):
        """Does the device need to be :obj:`home`\'d before a move can be performed?

        Returns
        -------
        :obj:`bool`
            Whether the device needs to be homed.
        """
        return self.sdk.CC_CanMoveWithoutHomingFirst(self._serial)

    def check_connection(self):
        """Check connection.

        Returns
        -------
        :obj:`bool`
            Whether the USB is listed by the FTDI controller.
        """
        return self.sdk.CC_CheckConnection(self._serial)

    def clear_message_queue(self):
        """Clears the device message queue."""
        self.sdk.CC_ClearMessageQueue(self._serial)

    def close(self):
        """Disconnect and close the device."""
        self.sdk.CC_Close(self._serial)

    def disable_channel(self):
        """Disable the channel so that motor can be moved by hand.

        When disabled, power is removed from the motor and it can be freely moved.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_DisableChannel(self._serial)

    def enable_channel(self):
        """Enable channel for computer control.

        When enabled, power is applied to the motor so it is fixed in position.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_EnableChannel(self._serial)

    def enable_last_msg_timer(self, enable, last_msg_timeout):
        """Enables the last message monitoring timer.

        This can be used to determine whether communications with the device is
        still good.

        Parameters
        ----------
        enable : :obj:`bool`
            :obj:`True` to enable monitoring otherwise :obj:`False` to disable.
        last_msg_timeout : :obj:`int`
            The last message error timeout in ms. Set to 0 to disable.
        """
        self.sdk.CC_EnableLastMsgTimer(self._serial, enable, last_msg_timeout)

    def get_backlash(self):
        """Get the backlash distance setting (used to control hysteresis).

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`int`
            The backlash distance in ``DeviceUnits`` (see manual).
        """
        return self.sdk.CC_GetBacklash(self._serial)

    def get_dc_pid_params(self):
        """Get the DC PID parameters for DC motors used in an algorithm involving calculus.

        Returns
        -------
        :class:`.structs.MOT_DC_PIDParameters`
             The DC PID parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        params = MOT_DC_PIDParameters()
        self.sdk.CC_GetDCPIDParams(self._serial, byref(params))
        return params

    def get_device_unit_from_real_value(self, real_value, unit_type):
        """Converts a real-world value to a device value.

        Either :meth:`load_settings` or :meth:`set_motor_params_ext` must be called before
        calling this function, otherwise the returned value will always be 0.

        Parameters
        ----------
        real_value : :obj:`float`
            The real-world value.
        unit_type : :class:`.enums.UnitType`
            The unit of the real-world value.

        Returns
        -------
        :obj:`int`
            The device value.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        device_unit = c_int()
        unit = self.convert_to_enum(unit_type, UnitType)
        self.sdk.CC_GetDeviceUnitFromRealValue(self._serial, real_value, byref(device_unit), unit)
        return device_unit.value

    def get_digital_outputs(self):
        """Gets the digital output bits.

        Returns
        -------
        :obj:`bytes`
            Bit mask of states of the 4 digital output pins.
        """
        return self.sdk.CC_GetDigitalOutputs(self._serial)

    def get_encoder_counter(self):
        """Get the encoder counter.

        For devices that have an encoder, the current encoder position can be read.

        Returns
        -------
        :obj:`int`
            The encoder count in encoder units.
        """
        return self.sdk.CC_GetEncoderCounter(self._serial)

    def get_hardware_info(self):
        """Gets the hardware information from the device.

        Returns
        -------
        :class:`.structs.TLI_HardwareInformation`
            The hardware information.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        return self._get_hardware_info(self.sdk.CC_GetHardwareInfo)

    def get_hardware_info_block(self):
        """Gets the hardware information in a block.

        Returns
        -------
        :class:`.structs.TLI_HardwareInformation`
            The hardware information.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        info = TLI_HardwareInformation()
        self.sdk.CC_GetHardwareInfoBlock(self._serial, byref(info))
        return info

    def get_homing_params_block(self):
        """Get the homing parameters.

        Returns
        -------
        :class:`.structs.MOT_HomingParameters`
            The homing parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        params = MOT_HomingParameters()
        self.sdk.CC_GetHomingParamsBlock(self._serial, byref(params))
        return params

    def get_homing_velocity(self):
        """Gets the homing velocity.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`int`
            The homing velocity in ``DeviceUnits`` (see manual).
        """
        return self.sdk.CC_GetHomingVelocity(self._serial)

    def get_hub_bay(self):
        """Gets the hub bay number this device is fitted to.

        Returns
        -------
        :obj:`bytes`
            The number, 0x00 if unknown or 0xff if not on a hub.
        """
        return self.sdk.CC_GetHubBay(self._serial)

    def get_jog_mode(self):
        """Gets the jog mode.

        Returns
        -------
        :class:`.enums.MOT_JogModes`
            The jog mode.
        :class:`.enums.MOT_StopModes`
            The stop mode.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        mode = c_short()
        stop_mode = c_short()
        self.sdk.CC_GetJogMode(self._serial, byref(mode), byref(stop_mode))
        return MOT_JogModes(mode.value), MOT_StopModes(mode.value)

    def get_jog_params_block(self):
        """Get the jog parameters.

        Returns
        -------
        :class:`.structs.MOT_JogParameters`
            The jog parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        params = MOT_JogParameters()
        self.sdk.CC_GetJogParamsBlock(self._serial, byref(params))
        return params

    def get_jog_step_size(self):
        """Gets the distance to move when jogging.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`int`
            The step size in ``DeviceUnits`` (see manual).
        """
        return self.sdk.CC_GetJogStepSize(self._serial)

    def get_jog_vel_params(self):
        """Gets the jog velocity parameters.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`int`
            The maximum velocity in ``DeviceUnits`` (see manual).
        :obj:`int`
            The acceleration in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        acceleration = c_int()
        max_velocity = c_int()
        self.sdk.CC_GetJogVelParams(self._serial, byref(acceleration), byref(max_velocity))
        return max_velocity.value, acceleration.value

    def get_led_switches(self):
        """Get the LED indicator bits on cube.

        Returns
        -------
        :obj:`int`
            Sum of: 8 to indicate moving 2 to indicate end of track and 1
            to flash on identify command.
        """
        return self.sdk.CC_GetLEDswitches(self._serial)

    def get_limit_switch_params(self):
        """ Gets the limit switch parameters.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :class:`.enums.MOT_LimitSwitchModes`
            The clockwise hardware limit mode.
        :class:`.enums.MOT_LimitSwitchModes`
            The anticlockwise hardware limit mode.
        :obj:`int`
            The position of the clockwise software limit in ``DeviceUnits`` (see manual).
        :obj:`int`
            The position of the anticlockwise software limit in ``DeviceUnits`` (see manual).
        :class:`.enums.MOT_LimitSwitchSWModes`
            The soft limit mode.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        cw_lim = WORD()
        ccw_lim = WORD()
        cw_pos = c_uint()
        ccw_pos = c_uint()
        soft = WORD()
        self.sdk.CC_GetLimitSwitchParams(self._serial, byref(cw_lim), byref(ccw_lim),
                                         byref(cw_pos), byref(ccw_pos), byref(soft))
        try:
            cw_mode = MOT_LimitSwitchModes(cw_lim.value)
        except ValueError:
            cw_mode = MOT_LimitSwitchModes(cw_lim.value | 0x0080)
        try:
            ccw_mode = MOT_LimitSwitchModes(ccw_lim.value)
        except ValueError:
            ccw_mode = MOT_LimitSwitchModes(ccw_lim.value | 0x0080)
        try:
            s_mode = MOT_LimitSwitchSWModes(soft.value)
        except ValueError:
            s_mode = MOT_LimitSwitchSWModes(soft.value | 0x0080)
        return cw_mode, ccw_mode, cw_pos.value, ccw_pos.value, s_mode

    def get_limit_switch_params_block(self):
        """Get the limit switch parameters.

        Returns
        -------
        :class:`.structs.MOT_LimitSwitchParameters`
            The limit switch parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        params = MOT_LimitSwitchParameters()
        self.sdk.CC_GetLimitSwitchParamsBlock(self._serial, byref(params))
        return params

    def get_mmi_params(self):
        """Get the MMI Parameters for the KCube Display Interface.

        Deprecated calls by :meth:`get_mmi_params_ext`
        """
        return self.get_mmi_params_ext()

    def get_mmi_params_block(self):
        """Gets the MMI parameters for the device.

        Returns
        -------
        :obj:`.structs.KMOT_MMIParams`
            The MMI parameters for the device.
        """
        mmi_params = KMOT_MMIParams()
        self.sdk.CC_GetMMIParamsBlock(self._serial, byref(mmi_params))
        return mmi_params

    def get_mmi_params_ext(self):
        """Get the MMI Parameters for the KCube Display Interface.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`.enums.KMOT_JoyStickMode`
            The device joystick mode.
        :obj:`int`
            The joystick maximum velocity in ``DeviceUnits``.
        :obj:`int`
            The joystick acceleration in ``DeviceUnits``.
        :obj:`.enums.KMOT_JoystickDirectionSense`
            The joystick direction sense.
        :obj:`int`
            The first preset position in ``DeviceUnits``.
        :obj:`int`
            The second preset position in ``DeviceUnits``.
        :obj:`int`
            The display intensity, range 0 to 100%.
        :obj:`int`
            The display timeout, range 0 to 480 in minutes (0 is off, otherwise
            the inactivity period before dimming the display).
        :obj:`int`
            The display dimmed intensity, range 0 to 10 (after the timeout
            period the device display will dim).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        mode = c_int16()
        vmax = c_int32()
        acc = c_int32()
        sense = c_int16()
        preset1 = c_int32()
        preset2 = c_int32()
        intensity = c_int16()
        timeout = c_int16()
        dim_intensity = c_int16()
        self.sdk.CC_GetMMIParamsExt(self._serial, byref(mode), byref(vmax), byref(acc), byref(sense), byref(preset1),
                                    byref(preset2), byref(intensity), byref(timeout), byref(dim_intensity))
        return (KMOT_JoyStickMode(mode.value), vmax.value, acc.value, KMOT_JoystickDirectionSense(sense.value),
                preset1.value, preset2.value, intensity.value, timeout.value, dim_intensity.value)

    def get_motor_params(self):
        """Gets the motor stage parameters.

        Deprecated: calls :meth:`get_motor_params_ext`

        These parameters, when combined define the stage motion in terms of
        ``RealWorldUnits`` [millimeters or degrees]. The real-world unit
        is defined from ``steps_per_rev * gear_box_ratio / pitch``.

        Returns
        ----------
        :obj:`float`
            The steps per revolution.
        :obj:`float`
            The gear box ratio.
        :obj:`float`
            The pitch.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        return self.get_motor_params_ext()

    def get_motor_params_ext(self):
        """Gets the motor stage parameters.

        These parameters, when combined define the stage motion in terms of
        ``RealWorldUnits`` [millimeters or degrees]. The real-world unit
        is defined from ``steps_per_rev * gear_box_ratio / pitch``.

        Returns
        ----------
        :obj:`float`
            The steps per revolution.
        :obj:`float`
            The gear box ratio.
        :obj:`float`
            The pitch.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        steps_per_rev = c_double()
        gear_box_ratio = c_double()
        pitch = c_double()
        self.sdk.CC_GetMotorParamsExt(self._serial, byref(steps_per_rev), byref(gear_box_ratio), byref(pitch))
        return steps_per_rev.value, gear_box_ratio.value, pitch.value

    def get_motor_travel_limits(self):
        """Gets the motor stage min and max position.

        Returns
        -------
        :obj:`float`
            The minimum position in ``RealWorldUnits`` [millimeters or degrees].
        :obj:`float`
            The maximum position in ``RealWorldUnits`` [millimeters or degrees].

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        min_position = c_double()
        max_position = c_double()
        self.sdk.CC_GetMotorTravelLimits(self._serial, byref(min_position), byref(max_position))
        return min_position.value, max_position.value

    def get_motor_travel_mode(self):
        """Get the motor travel mode.

        Returns
        -------
        :class:`.enums.MOT_TravelModes`
            The travel mode.
        """
        return MOT_TravelModes(self.sdk.CC_GetMotorTravelMode(self._serial))

    def get_motor_velocity_limits(self):
        """Gets the motor stage maximum velocity and acceleration.

        Returns
        -------
        :obj:`float`
            The maximum velocity in ``RealWorldUnits`` [millimeters or degrees].
        :obj:`float`
            The maximum acceleration in ``RealWorldUnits`` [millimeters or degrees].

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        max_velocity = c_double()
        max_acceleration = c_double()
        self.sdk.CC_GetMotorVelocityLimits(self._serial, byref(max_velocity), byref(max_acceleration))
        return max_velocity.value, max_acceleration.value

    def get_move_absolute_position(self):
        """Gets the move absolute position.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`int`
            The move absolute position in ``DeviceUnits`` (see manual).
        """
        return self.sdk.CC_GetMoveAbsolutePosition(self._serial)

    def get_move_relative_distance(self):
        """Gets the move relative distance.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`int`
            The move relative position in ``DeviceUnits`` (see manual).
        """
        return self.sdk.CC_GetMoveRelativeDistance(self._serial)

    def get_next_message(self):
        """Get the next Message Queue item. See :mod:`.messages`.

        Returns
        -------
        :obj:`int`
            The message type.
        :obj:`int`
            The message ID.
        :obj:`int`
            The message data.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        message_type = WORD()
        message_id = WORD()
        message_data = DWORD()
        self.sdk.CC_GetNextMessage(self._serial, byref(message_type), byref(message_id), byref(message_data))
        return message_type.value, message_id.value, message_data.value

    def get_number_positions(self):
        """Get the number of positions.

        This function will get the maximum position reachable by the device.
        The motor may need to be set to its :meth:`home` position before this
        parameter can be used.

        Returns
        -------
        :obj:`int`
            The number of positions.
        """
        return self.sdk.CC_GetNumberPositions(self._serial)

    def get_position(self):
        """Get the current position.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        index : :obj:`int`
            The position in ``DeviceUnits`` (see manual).
        """
        return self.sdk.CC_GetPosition(self._serial)

    def get_position_counter(self):
        """Get the position counter.

        The position counter is identical to the position parameter.
        The position counter is set to zero when homing is complete.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`int`
            The position counter in ``DeviceUnits`` (see manual).
        """
        return self.sdk.CC_GetPositionCounter(self._serial)

    def get_real_value_from_device_unit(self, device_value, unit_type):
        """Converts a device value to a real-world value.

        Either :meth:`load_settings` or :meth:`set_motor_params_ext` must be called before
        calling this function, otherwise the returned value will always be 0.0.

        Parameters
        ----------
        device_value : :obj:`int`
            The device value.
        unit_type : :class:`.enums.UnitType`
            The unit of the device value.

        Returns
        -------
        :obj:`float`
            The real-world value.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        real_unit = c_double()
        unit = self.convert_to_enum(unit_type, UnitType)
        self.sdk.CC_GetRealValueFromDeviceUnit(self._serial, device_value, byref(real_unit), unit)
        return real_unit.value

    def get_soft_limit_mode(self):
        """Gets the software limits mode.

        Returns
        -------
        :class:`.enums.MOT_LimitsSoftwareApproachPolicy`
            The software limits mode.
        """
        return MOT_LimitsSoftwareApproachPolicy(self.sdk.CC_GetSoftLimitMode(self._serial))

    def get_software_version(self):
        """Gets version number of the device software.

        Returns
        -------
        :obj:`str`
            The device software version.
        """
        return self.to_version(self.sdk.CC_GetSoftwareVersion(self._serial))

    def get_stage_axis_max_pos(self):
        """Gets the Stepper Motor maximum stage position.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`int`
            The maximum position in ``DeviceUnits`` (see manual).
        """
        return self.sdk.CC_GetStageAxisMaxPos(self._serial)

    def get_stage_axis_min_pos(self):
        """Gets the Stepper Motor minimum stage position.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`int`
            The minimum position in ``DeviceUnits`` (see manual).
        """
        return self.sdk.CC_GetStageAxisMinPos(self._serial)

    def get_status_bits(self):
        """Get the current status bits.

        This returns the latest status bits received from the device.
        To get new status bits, use :meth:`request_status_bits` or use
        the polling functions, :meth:`start_polling`.

        Returns
        -------
        :obj:`int`
            The status bits from the device.
        """
        return self.sdk.CC_GetStatusBits(self._serial)

    def get_trigger_config_params(self):
        """Get the Trigger Configuration Parameters.

        Returns
        -------
        :class:`.enums.KMOT_TriggerPortMode`
            The trigger 1 mode.
        :class:`.enums.KMOT_TriggerPortPolarity`
            The trigger 1 polarity.
        :class:`.enums.KMOT_TriggerPortMode`
            The trigger 2 mode.
        :class:`.enums.KMOT_TriggerPortPolarity`
            The trigger 2 polarity.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        mode1 = c_int16()
        pol1 = c_int16()
        mode2 = c_int16()
        pol2 = c_int16()
        self.sdk.CC_GetTriggerConfigParams(self._serial, byref(mode1), byref(pol1), byref(mode2), byref(pol2))
        return (KMOT_TriggerPortMode(mode1.value), KMOT_TriggerPortPolarity(pol1.value),
                KMOT_TriggerPortMode(mode2.value), KMOT_TriggerPortPolarity(pol2.value))

    def get_trigger_config_params_block(self):
        """Gets the trigger configuration parameters block.

        Returns
        -------
        :class:`.structs.KMOT_TriggerConfig`
            Options for controlling the trigger configuration.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        params = KMOT_TriggerConfig()
        self.sdk.CC_GetTriggerConfigParamsBlock(self._serial, byref(params))
        return params

    def get_trigger_params_params(self):
        """Get the Trigger Parameters parameters.

        See :obj:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        :obj:`int`
            The trigger start position, forward, in ``DeviceUnits`` (see manual).
        :obj:`int`
            The trigger interval, forward, in ``DeviceUnits`` (see manual).
        :obj:`int`
            Number of trigger pulses, forward.
        :obj:`int`
            The trigger start position, reverse, in ``DeviceUnits`` (see manual).
        :obj:`int`
            The trigger interval, reverse, in ``DeviceUnits`` (see manual).
        :obj:`int`
            Number of trigger pulses, reverse.
        :obj:`int`
            Width of the trigger pulse in milliseconds, range 10 (10us) to 650000 (650ms).
        :obj:`int`
            Number of cycles to perform triggering.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        trigger_start_position_fwd = c_int32()
        trigger_interval_fwd = c_int32()
        trigger_pulse_count_fwd = c_int32()
        trigger_start_position_rev = c_int32()
        trigger_interval_rev = c_int32()
        trigger_pulse_count_rev = c_int32()
        trigger_pulse_width = c_int32()
        cycle_count = c_int32()
        self.sdk.CC_GetTriggerParamsParams(self._serial, byref(trigger_start_position_fwd),
                                           byref(trigger_interval_fwd), byref(trigger_pulse_count_fwd),
                                           byref(trigger_start_position_rev), byref(trigger_interval_rev),
                                           byref(trigger_pulse_count_rev), byref(trigger_pulse_width),
                                           byref(cycle_count))
        return (trigger_start_position_fwd.value, trigger_interval_fwd.value, trigger_pulse_count_fwd.value,
                trigger_start_position_rev.value, trigger_interval_rev.value, trigger_pulse_count_rev.value,
                trigger_pulse_width.value, cycle_count.value)

    def get_trigger_params_params_block(self):
        """Gets the trigger parameters block.

        Returns
        -------
        :obj:`.structs.KMOT_TriggerParams`
            Options for controlling the trigger.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        params = KMOT_TriggerParams()
        self.sdk.CC_GetTriggerParamsParamsBlock(self._serial, byref(params))
        return params

    def get_vel_params(self):
        """Gets the move velocity parameters.

        See :meth:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Returns
        -------
        max_velocity : :obj:`int`
            The maximum velocity in ``DeviceUnits`` (see manual).
        acceleration : :obj:`int`
            The acceleration in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        acceleration = c_int()
        max_velocity = c_int()
        self.sdk.CC_GetVelParams(self._serial, byref(acceleration), byref(max_velocity))
        return max_velocity.value, acceleration.value

    def get_vel_params_block(self):
        """Get the move velocity parameters.

        Returns
        -------
        :class:`.structs.MOT_VelocityParameters`
            The velocity parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        params = MOT_VelocityParameters()
        self.sdk.CC_GetVelParamsBlock(self._serial, byref(params))
        return params

    def has_last_msg_timer_overrun(self):
        """Queries if the time since the last message has exceeded the
        ``lastMsgTimeout`` set by :meth:`.enable_last_msg_timer`.

        This can be used to determine whether communications with the device is
        still good.

        Returns
        -------
        :obj:`bool`
            :obj:`True` if last message timer has elapsed or
            :obj:`False` if monitoring is not enabled or if time of last message
            received is less than ``lastMsgTimeout``.
        """
        return self.sdk.CC_HasLastMsgTimerOverrun(self._serial)

    def home(self, wait=True):
        """Home the device.

        Homing the device will set the device to a known state and determine
        the home position.

        Parameters
        ----------
        wait : :obj:`bool`
            Wait until the device has been homed before returning to the
            calling program.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_Home(self._serial)
        if wait:
            self._wait(0)
            assert self.get_position() == 0, 'Wait until homed is not working'

    def identify(self):
        """Sends a command to the device to make it identify itself."""
        self.sdk.CC_Identify(self._serial)

    def load_settings(self):
        """Update device with stored settings.

        The settings are read from ``ThorlabsDefaultSettings.xml``, which
        gets created when the Kinesis software is installed.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        if not self.sdk.CC_LoadSettings(self._serial):
            self.raise_exception('Error loading the stored settings.')

    def message_queue_size(self):
        """Gets the size of the message queue.

        Returns
        -------
        :obj:`int`
            The number of messages in the queue.
        """
        return self.sdk.CC_MessageQueueSize(self._serial)

    def move_absolute(self):
        """Moves the device to the position defined in :meth:`set_move_absolute_position`.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_MoveAbsolute(self._serial)

    def move_at_velocity(self, direction):
        """Start moving at the current velocity in the specified direction.

        Parameters
        ----------
        direction : :class:`.enums.MOT_TravelDirection`
            The required direction of travel as a :class:`.enums.MOT_TravelDirection`
            enum value or member name.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_MoveAtVelocity(self._serial, direction)

    def move_jog(self, jog_direction):
        """Perform a jog.

        Parameters
        ----------
        jog_direction : :class:`.enums.MOT_TravelDirection`
            The jog direction as a :class:`.enums.MOT_TravelDirection` enum value
            or member name.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        direction = self.convert_to_enum(jog_direction, MOT_TravelDirection, prefix='MOT_')
        self.sdk.CC_MoveJog(self._serial, direction)

    def move_relative(self, displacement):
        """Move the motor by a relative amount.

        See :meth:`get_device_unit_from_real_value`:meth:`get_device_unit_from_real_value` for
        converting from a ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        displacement : :obj:`int`
            Signed displacement in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_MoveRelative(self._serial, displacement)

    def move_relative_distance(self):
        """Moves the device by a relative distance defined by :meth:`set_move_relative_distance`.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_MoveRelativeDistance(self._serial)

    def move_to_position(self, index, wait=True):
        """Move the device to the specified position (index).

        The motor may need to be set to its :meth:`home` position before a
        position can be set.

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        index : :obj:`int`
            The position in ``DeviceUnits`` (see manual).
        wait : :obj:`bool`
            Wait until the device has finished moving before returning to the
            calling program.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_MoveToPosition(self._serial, index)
        if wait:
            self._wait(1)
            assert self.get_position() == index, 'Wait until move finished is not working'

    def needs_homing(self):
        """Does the device need to be :obj:`home`\'d before a move can be performed?

        Deprecated: calls :meth:`can_move_without_homing_first` instead.

        Returns
        -------
        :obj:`bool`
            Whether the device needs to be homed.
        """
        return self.sdk.can_move_without_homing_first()

    def open(self):
        """Open the device for communication.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_Open(self._serial)

    def persist_settings(self):
        """Persist the devices current settings.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        if not self.sdk.CC_PersistSettings(self._serial):
            self.raise_exception('Error to persist the current settings.')

    def polling_duration(self):
        """Gets the polling loop duration.

        Returns
        -------
        :obj:`int`
            The time between polls in milliseconds or 0 if polling is not active.
        """
        return self.sdk.CC_PollingDuration(self._serial)

    def register_message_callback(self, callback):
        """Registers a callback on the message queue.

        Parameters
        ----------
        callback : :obj:`.callbacks.MotionControlCallback`
            A function to be called whenever messages are received.
        """
        self.sdk.CC_RegisterMessageCallback(self._serial, callback)

    def request_backlash(self):
        """Requests the backlash.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestBacklash(self._serial)

    def request_dc_pid_params(self):
        """Request the PID parameters for DC motors used in an algorithm involving calculus.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestDCPIDParams(self._serial)

    def request_digital_outputs(self):
        """Requests the digital output bits.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestDigitalOutputs(self._serial)

    def request_encoder_counter(self):
        """Requests the encoder counter.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestEncoderCounter(self._serial)

    def request_homing_params(self):
        """Requests the homing parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestHomingParams(self._serial)

    def request_jog_params(self):
        """Requests the jog parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestJogParams(self._serial)

    def request_led_switches(self):
        """Requests the LED indicator bits on the cube.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestLEDswitches(self._serial)

    def request_limit_switch_params(self):
        """Requests the limit switch parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestLimitSwitchParams(self._serial)

    def request_mmi_params(self):
        """Requests the MMI Parameters for the KCube Display Interface.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestMMIparams(self._serial)

    def request_move_absolute_position(self):
        """Requests the position of next absolute move.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestMoveAbsolutePosition(self._serial)

    def request_move_relative_distance(self):
        """Requests the relative move distance.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestMoveRelativeDistance(self._serial)

    def request_pos_trigger_params(self):
        """Requests the position trigger parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestPosTriggerParams(self._serial)

    def request_position(self):
        """Requests the current position.

        This needs to be called to get the device to send it's current position.
        Note, this is called automatically if ``Polling`` is enabled for the device
        using :meth:`start_polling`.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestPosition(self._serial)

    def request_settings(self):
        """Requests that all settings are downloaded from the device.

        This function requests that the device upload all it's settings to the
        DLL.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestSettings(self._serial)

    def request_status_bits(self):
        """Request the status bits which identify the current motor state.

        This needs to be called to get the device to send it's current status bits.
        Note, this is called automatically if ``Polling`` is enabled for the device
        using :meth:`start_polling`.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestStatusBits(self._serial)

    def request_trigger_config_params(self):
        """Requests the Trigger Configuration Parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestTriggerConfigParams(self._serial)

    def request_vel_params(self):
        """Requests the velocity parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_RequestVelParams(self._serial)

    def reset_stage_to_defaults(self):
        """Reset the stage settings to defaults.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        if not self.sdk.CC_ResetStageToDefaults(self._serial):
            self.raise_exception('Cannot reset stage to defaults')

    def resume_move_messages(self):
        """Resume suspended move messages.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_ResumeMoveMessages(self._serial)

    def set_backlash(self, distance):
        """Sets the backlash distance (used to control hysteresis).

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        distance : :obj:`int`
            The backlash distance in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetBacklash(self._serial, distance)

    def set_dc_pid_params(self, params):
        """Set the PID parameters for DC motors used in an algorithm involving calculus.

        Parameters
        ----------
        params : :class:`.structs.MOT_DC_PIDParameters`
            The DC PID parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        TypeError
            If the data type of `params` is not :class:`.structs.MOT_DC_PIDParameters`
        """
        if not isinstance(params, MOT_DC_PIDParameters):
            raise TypeError('The DC PID parameter must be a MOT_DC_PIDParameters struct')
        self.sdk.CC_SetDCPIDParams(self._serial, byref(params))

    def set_digital_outputs(self, outputs_bits):
        """Sets the digital output bits.

        Parameters
        ----------
        outputs_bits : :obj:`int`
            Bit mask to set the states of the 4 digital output pins.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetDigitalOutputs(self._serial, outputs_bits)

    def set_direction(self, reverse):
        """Sets the motor direction sense.

        This function is used because some actuators have directions of motion
        reversed. This parameter will tell the system to reverse the direction sense
        when moving, jogging etc.

        Parameters
        ----------
        reverse : :obj:`bool`
            If :obj:`True` then directions will be swapped on these moves.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetDirection(self._serial, reverse)

    def set_encoder_counter(self, count):
        """Set the Encoder Counter values.

        Setting the encoder counter to zero, effectively defines a home position on the encoder strip.
        Note, setting this value does not move the device.

        Parameters
        ----------
        count : :obj:`int`
            The encoder count in encoder units.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetEncoderCounter(self._serial, count)

    def set_homing_params_block(self, direction, limit, velocity, offset):
        """Set the homing parameters.

        Parameters
        ----------
        direction : :class:`.enums.MOT_TravelDirection`
            The Homing direction sense as a :class:`.enums.MOT_TravelDirection`
            enum value or member name.
        limit : :class:`.enums.MOT_HomeLimitSwitchDirection`
            The limit switch direction as a :class:`.enums.MOT_HomeLimitSwitchDirection`
            enum value or member name.
        velocity : :obj:`int`
            The velocity in small indivisible units.
        offset : :obj:`int`
            Distance of home from limit in small indivisible units.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        params = MOT_HomingParameters()
        params.direction = self.convert_to_enum(direction, MOT_TravelDirection, prefix='MOT_')
        params.limitSwitch = self.convert_to_enum(limit, MOT_HomeLimitSwitchDirection, prefix='MOT_')
        params.velocity = velocity
        params.offsetDistance = offset
        self.sdk.CC_SetHomingParamsBlock(self._serial, byref(params))

    def set_homing_velocity(self, velocity):
        """Sets the homing velocity.

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        velocity : :obj:`int`
            The homing velocity in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetHomingVelocity(self._serial, velocity)

    def set_jog_mode(self, mode, stop_mode):
        """Sets the jog mode.

        Parameters
        ----------
        mode : :class:`.enums.MOT_JogModes`
            The jog mode, as a :class:`.enums.MOT_JogModes` enum value or member name.

        stop_mode : :class:`.enums.MOT_StopModes`
            The stop mode, as a :class:`.enums.MOT_StopModes` enum value or member name.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        mode_ = self.convert_to_enum(mode, MOT_JogModes, prefix='MOT_')
        stop_mode_ = self.convert_to_enum(stop_mode, MOT_StopModes, prefix='MOT_')
        self.sdk.CC_SetJogMode(self._serial, mode_, stop_mode_)

    def set_jog_params_block(self, jog_params):
        """Set the jog parameters.

        Parameters
        ----------
        jog_params : :class:`.structs.MOT_JogParameters`
            The jog parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        TypeError
            If the data type of `jog_params` is not :class:`.structs.MOT_JogParameters`
        """
        if not isinstance(jog_params, MOT_JogParameters):
            raise TypeError('The jog parameter must be a MOT_JogParameters struct')
        return self.sdk.CC_SetJogParamsBlock(self._serial, byref(jog_params))

    def set_jog_step_size(self, step_size):
        """Sets the distance to move on jogging.

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        step_size : :obj:`int`
            The step size in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetJogStepSize(self._serial, step_size)

    def set_jog_vel_params(self, max_velocity, acceleration):
        """Sets jog velocity parameters.

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        max_velocity : :obj:`int`
            The maximum velocity in ``DeviceUnits`` (see manual).
        acceleration : :obj:`int`
            The acceleration in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetJogVelParams(self._serial, acceleration, max_velocity)

    def set_led_switches(self, led_switches):
        """Set the LED indicator bits on the cube.

        Parameters
        ----------
        led_switches : :obj:`int`
            Sum of: 8 to indicate moving 2 to indicate end of track and
            1 to flash on identify command.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetLEDswitches(self._serial, led_switches)

    def set_limit_switch_params(self, cw_lim, ccw_lim, cw_pos, ccw_pos, soft_limit_mode):
        """Sets the limit switch parameters.

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        cw_lim : :class:`.enums.MOT_LimitSwitchModes`
            The clockwise hardware limit mode as a :class:`.enums.MOT_LimitSwitchModes`
            enum value or member name.
        ccw_lim : :class:`.enums.MOT_LimitSwitchModes`
            The anticlockwise hardware limit mode as a :class:`.enums.MOT_LimitSwitchModes`
            enum value or member name.
        cw_pos : :obj:`int`
            The position of the clockwise software limit in ``DeviceUnits`` (see manual).
        ccw_pos : :obj:`int`
            The position of the anticlockwise software limit in ``DeviceUnits`` (see manual).
        soft_limit_mode : :class:`.enums.MOT_LimitSwitchSWModes`
            The soft limit mode as a :class:`.enums.MOT_LimitSwitchSWModes` enum
            value or member name.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        cw_lim_ = self.convert_to_enum(cw_lim, MOT_LimitSwitchModes, prefix='MOT_')
        ccw_lim_ = self.convert_to_enum(ccw_lim, MOT_LimitSwitchModes, prefix='MOT_')
        sw = self.convert_to_enum(soft_limit_mode, MOT_LimitSwitchSWModes, prefix='MOT_')
        self.sdk.CC_SetLimitSwitchParams(self._serial, cw_lim_, ccw_lim_, cw_pos, ccw_pos, sw)

    def set_limit_switch_params_block(self, params):
        """Set the limit switch parameters.

        Parameters
        ----------
        params : :class:`.structs.MOT_LimitSwitchParameters`
            The limit switch parameters.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        if not isinstance(params, MOT_LimitSwitchParameters):
            raise TypeError('The limit switch parameter must be a MOT_LimitSwitchParameters struct')
        self.sdk.CC_SetLimitSwitchParamsBlock(self._serial, byref(params))

    def set_limits_software_approach_policy(self, policy):
        """Sets the software limits mode.

        Parameters
        ----------
        policy : :class:`.enums.MOT_LimitsSoftwareApproachPolicy`
            The soft limit mode as a :class:`.enums.MOT_LimitsSoftwareApproachPolicy` enum
            value or member name.
        """
        policy_ = self.convert_to_enum(policy, MOT_LimitsSoftwareApproachPolicy)
        self.sdk.CC_SetLimitsSoftwareApproachPolicy(self._serial, policy_)

    def set_mmi_params(self, joystick_mode, joystick_max_velocity, joystick_acceleration,
                       direction_sense, preset_position1, preset_position2, display_intensity):
        """Set the MMI Parameters for the KCube Display Interface.

        Deprecated calls :meth:`set_mmi_params_ext` setting the `display_timeout` to 1 minute
        and the `display_dim_intensity` to 8.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        return self.set_mmi_params_ext(joystick_mode, joystick_max_velocity, joystick_acceleration, direction_sense,
                                       preset_position1, preset_position2, display_intensity, 1, 8)

    def set_mmi_params_block(self, mmi_params):
        """Sets the MMI parameters for the device.

        Parameters
        ----------
        mmi_params : :class:`.structs.KMOT_MMIParams`
            Options for controlling the mmi.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        if not isinstance(mmi_params, KMOT_MMIParams):
            self.raise_exception('Must pass in a KMOT_MMIParams structure')
        self.sdk.CC_SetMMIParamsBlock(self._serial, byref(mmi_params))

    def set_mmi_params_ext(self, joystick_mode, joystick_max_velocity, joystick_acceleration, direction_sense,
                           preset_position1, preset_position2, display_intensity, display_timeout,
                           display_dim_intensity):
        """Set the MMI Parameters for the KCube Display Interface.

        See :meth:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Parameters
        ----------
        joystick_mode : :obj:`.enums.KMOT_JoyStickMode`
            The device joystick mode as a :obj:`.enums.KMOT_JoyStickMode` enum value or member name.
        joystick_max_velocity : :obj:`int`
            The joystick maximum velocity in ``DeviceUnits``.
        joystick_acceleration : :obj:`int`
            The joystick acceleration in ``DeviceUnits``.
        direction_sense : :obj:`.enums.KMOT_JoystickDirectionSense`
            The joystick direction sense as a :obj:`.enums.KMOT_JoystickDirectionSense` enum value or member name.
        preset_position1 : :obj:`int`
            The first preset position in ``DeviceUnits``.
        preset_position2 : :obj:`int`
            The second preset position in ``DeviceUnits``.
        display_intensity : :obj:`int`
            The display intensity, range 0 to 100%.
        display_timeout : :obj:`int`
            The display timeout, range 0 to 480 in minutes (0 is off, otherwise
            the inactivity period before dimming the display).
        display_dim_intensity : :obj:`int`
            The display dimmed intensity, range 0 to 10 (after the timeout
            period the device display will dim).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        mode = self.convert_to_enum(joystick_mode, KMOT_JoyStickMode, prefix='KMOT_JS_')
        sense = self.convert_to_enum(direction_sense, KMOT_JoystickDirectionSense, prefix='KMOT_JS_')
        self.sdk.CC_SetMMIParamsExt(self._serial, mode, joystick_max_velocity, joystick_acceleration, sense,
                                    preset_position1, preset_position2, display_intensity, display_timeout,
                                    display_dim_intensity)

    def set_motor_params(self, steps_per_rev, gear_box_ratio, pitch):
        """Sets the motor stage parameters.

        Deprecated: calls :meth:`set_motor_params_ext`

        These parameters, when combined, define the stage motion in terms of
        ``RealWorldUnits`` [millimeters or degrees]. The real-world unit
        is defined from ``steps_per_rev * gear_box_ratio / pitch``.

        See :meth:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Parameters
        ----------
        steps_per_rev : :obj:`float`
            The steps per revolution.
        gear_box_ratio : :obj:`float`
            The gear box ratio.
        pitch : :obj:`float`
            The pitch.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.set_motor_params_ext(steps_per_rev, gear_box_ratio, pitch)

    def set_motor_params_ext(self, steps_per_rev, gear_box_ratio, pitch):
        """Sets the motor stage parameters.

        These parameters, when combined, define the stage motion in terms of
        ``RealWorldUnits`` [millimeters or degrees]. The real-world unit
        is defined from ``steps_per_rev * gear_box_ratio / pitch``.

        See :meth:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Parameters
        ----------
        steps_per_rev : :obj:`float`
            The steps per revolution.
        gear_box_ratio : :obj:`float`
            The gear box ratio.
        pitch : :obj:`float`
            The pitch.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetMotorParamsExt(self._serial, steps_per_rev, gear_box_ratio, pitch)

    def set_motor_travel_limits(self, min_position, max_position):
        """Sets the motor stage min and max position.

        These define the range of travel for the stage.

        See :meth:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Parameters
        ----------
        min_position : :obj:`float`
            The minimum position in ``RealWorldUnits`` [millimeters or degrees].
        max_position : :obj:`float`
            The maximum position in ``RealWorldUnits`` [millimeters or degrees].

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetMotorTravelLimits(self._serial, min_position, max_position)

    def set_motor_travel_mode(self, travel_mode):
        """Set the motor travel mode.

        Parameters
        ----------
        travel_mode : :class:`.enums.MOT_TravelModes`
            The travel mode as a :class:`.enums.MOT_TravelModes` enum value or
            member name.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        mode = self.convert_to_enum(travel_mode, MOT_TravelModes, prefix='MOT_')
        self.sdk.CC_SetMotorTravelMode(self._serial, mode)

    def set_motor_velocity_limits(self, max_velocity, max_acceleration):
        """Sets the motor stage maximum velocity and acceleration.

        See :meth:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Parameters
        ----------
        max_velocity : :obj:`float`
            The maximum velocity in ``RealWorldUnits`` [millimeters or degrees].
        max_acceleration : :obj:`float`
            The maximum acceleration in ``RealWorldUnits`` [millimeters or degrees].

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetMotorVelocityLimits(self._serial, max_velocity, max_acceleration)

    def set_move_absolute_position(self, position):
        """Sets the move absolute position.

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        position : :obj:`int`
            The absolute position in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetMoveAbsolutePosition(self._serial, position)

    def set_move_relative_distance(self, distance):
        """Sets the move relative distance.

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        distance : :obj:`int`
            The relative position in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetMoveRelativeDistance(self._serial, distance)

    def set_position_counter(self, count):
        """Set the position counter.

        Setting the position counter will locate the current position.
        Setting the position counter will effectively define the home position
        of a motor.

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        count : :obj:`int`
            The position counter in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetPositionCounter(self._serial, count)

    def set_stage_axis_limits(self, min_position, max_position):
        """Sets the stage axis position limits.

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        min_position : :obj:`int`
            The minimum position in ``DeviceUnits`` (see manual).
        max_position : :obj:`int`
            The maximum position in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetStageAxisLimits(self._serial, min_position, max_position)

    def set_trigger_config_params(self, mode1, polarity1, mode2, polarity2):
        """Set the trigger configuration parameters.

        Parameters
        ----------
        mode1 : :class:`.enums.KMOT_TriggerPortMode`
            The trigger 1 mode as a :class:`~.enums.KMOT_TriggerPortMode` enum
            value or member name.
        polarity1 : :class:`.enums.KMOT_TriggerPortPolarity`
            The trigger 1 polarity as a :class:`~.enums.KMOT_TriggerPortPolarity`
            enum value or member name.
        mode2 : :class:`.enums.KMOT_TriggerPortMode`
            The trigger 2 mode as a :class:`~.enums.KMOT_TriggerPortMode` enum
            value or member name.
        polarity2 : :class:`.enums.KMOT_TriggerPortPolarity`
            The trigger 2 polarity as a :class:`~.enums.KMOT_TriggerPortPolarity`
            enum value or member name.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        m1 = self.convert_to_enum(mode1, KMOT_TriggerPortMode, prefix='KMOT_')
        p1 = self.convert_to_enum(polarity1, KMOT_TriggerPortPolarity, prefix='KMOT_')
        m2 = self.convert_to_enum(mode2, KMOT_TriggerPortMode, prefix='KMOT_')
        p2 = self.convert_to_enum(polarity2, KMOT_TriggerPortPolarity, prefix='KMOT_')
        self.sdk.CC_SetTriggerConfigParams(self._serial, m1, p1, m2, p2)

    def set_trigger_config_params_block(self, trigger_config_params):
        """Sets the trigger configuration parameters block.

        Parameters
        ----------
        trigger_config_params : :class:`.structs.KMOT_TriggerConfig`
            Options for controlling the trigger configuration.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        :exc:`TypeError`
            If `trigger_config_params` is not a :class:`.structs.KMOT_TriggerConfig`.
        """
        if not isinstance(trigger_config_params, KMOT_TriggerConfig):
            self.raise_exception('Must pass in a KMOT_TriggerConfig structure')
        self.sdk.CC_SetTriggerConfigParamsBlock(self._serial, byref(trigger_config_params))

    def set_trigger_params_params(self, trigger_start_position_fwd, trigger_interval_fwd, trigger_pulse_count_fwd,
                                  trigger_start_position_rev, trigger_interval_rev, trigger_pulse_count_rev,
                                  trigger_pulse_width, cycle_count):
        """Set the Trigger Parameters parameters.

        See :meth:`get_real_value_from_device_unit` for converting from a
        ``DeviceUnit`` to a ``RealValue``.

        Parameters
        ----------
        trigger_start_position_fwd : :obj:`int`
            The trigger start position, forward, in ``DeviceUnits`` (see manual).
        trigger_interval_fwd : :obj:`int`
            The trigger interval, forward, in ``DeviceUnits`` (see manual).
        trigger_pulse_count_fwd : :obj:`int`
            Number of trigger pulses, forward.
        trigger_start_position_rev : :obj:`int`
            The trigger start position, reverse, in ``DeviceUnits`` (see manual).
        trigger_interval_rev : :obj:`int`
            The trigger interval, reverse, in ``DeviceUnits`` (see manual).
        trigger_pulse_count_rev : :obj:`int`
            Number of trigger pulses., reverse.
        trigger_pulse_width : :obj:`int`
            Width of the trigger pulse in milliseconds, range 10 (10us) to 650000 (650ms).
        cycle_count : :obj:`int`
            Number of cycles to perform triggering.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetTriggerParamsParams(self._serial, trigger_start_position_fwd, trigger_interval_fwd,
                                           trigger_pulse_count_fwd, trigger_start_position_rev, trigger_interval_rev,
                                           trigger_pulse_count_rev, trigger_pulse_width, cycle_count)

    def set_trigger_params_params_block(self, trigger_params_params):
        """Set the Trigger Parameters parameters.

        Parameters
        ----------
        trigger_params_params : :class:`.structs.KMOT_TriggerParams`
            Options for controlling the trigger.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        :exc:`TypeError`
            If `trigger_params_params` is not a :class:`.structs.KMOT_TriggerParams`.
        """
        if not isinstance(trigger_params_params, KMOT_TriggerParams):
            self.raise_exception('Must pass in a KMOT_TriggerParams structure')
        self.sdk.CC_SetTriggerParamsParamsBlock(self._serial, byref(trigger_params_params))

    def set_vel_params(self, max_velocity, acceleration):
        """Sets the move velocity parameters.

        See :meth:`get_device_unit_from_real_value` for converting from a
        ``RealValue`` to a ``DeviceUnit``.

        Parameters
        ----------
        max_velocity : :obj:`int`
            The maximum velocity in ``DeviceUnits`` (see manual).
        acceleration : :obj:`int`
            The acceleration in ``DeviceUnits`` (see manual).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SetVelParams(self._serial, acceleration, max_velocity)

    def set_vel_params_block(self, min_velocity, max_velocity, acceleration):
        """Set the move velocity parameters.

        Parameters
        ----------
        min_velocity : :obj:`int`
            The minimum velocity.
        max_velocity : :obj:`int`
            The maximum velocity.
        acceleration : :obj:`int`
            The acceleration.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        params = MOT_VelocityParameters()
        params.minVelocity = min_velocity
        params.acceleration = acceleration
        params.maxVelocity = max_velocity
        self.sdk.CC_SetVelParamsBlock(self._serial, byref(params))

    def start_polling(self, milliseconds):
        """Starts the internal polling loop.

        This function continuously requests position and status messages.

        Parameters
        ----------
        milliseconds : :obj:`int`
            The polling rate, in milliseconds.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_StartPolling(self._serial, milliseconds)

    def stop_immediate(self):
        """Stop the current move immediately (with the risk of losing track of the position).

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_StopImmediate(self._serial)

    def stop_polling(self):
        """Stops the internal polling loop."""
        self.sdk.CC_StopPolling(self._serial)

    def stop_profiled(self):
        """Stop the current move using the current velocity profile.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_StopProfiled(self._serial)

    def suspend_move_messages(self):
        """Suspend automatic messages at ends of moves.

        Useful to speed up part of real-time system with lots of short moves.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        self.sdk.CC_SuspendMoveMessages(self._serial)

    def time_since_last_msg_received(self):
        """Gets the time, in milliseconds, since the last message was received.

        This can be used to determine whether communications with the device is
        still good.

        Returns
        -------
        :obj:`int`
            The time, in milliseconds, since the last message was received.
        """
        ms = c_int64()
        self.sdk.CC_TimeSinceLastMsgReceived(self._serial, byref(ms))
        return ms.value

    def wait_for_message(self):
        """Wait for next Message Queue item. See :mod:`.messages`.

        Returns
        -------
        :obj:`int`
            The message type.
        :obj:`int`
            The message ID.
        :obj:`int`
            The message data.

        Raises
        ------
        :exc:`~msl.equipment.exceptions.ThorlabsError`
            If not successful.
        """
        message_type = WORD()
        message_id = WORD()
        message_data = DWORD()
        self.sdk.CC_WaitForMessage(self._serial, byref(message_type), byref(message_id), byref(message_data))
        return message_type.value, message_id.value, message_data.value


if __name__ == '__main__':
    from msl.equipment.resources.utils import camelcase_to_underscore as convert

    for item in sorted(KCube_DCServo_FCNS):
        method_name = convert(item[0].split('_')[1])
        args_p = ''
        args_c = ''
        for i, arg in enumerate(item[3]):
            if i == 0 and 'c_char_p' in str(arg[0]):
                args_c += 'self._serial, '
            elif 'PyCPointerType' in str(type(arg[0])):
                args_c += 'byref({}), '.format(convert(arg[1]))
            else:
                a = convert(arg[1])
                args_p += '{}, '.format(a)
                args_c += '{}, '.format(a)

        args_p = args_p[:-2]
        if args_p:
            print('    def {}(self, {}):'.format(method_name, args_p))
        else:
            print('    def {}(self):'.format(method_name))
        print('        return self.sdk.{}({})\n'.format(item[0], args_c[:-2]))
