import time
import math
import threading

import pytest
import pyvisa

from msl.loadlib import IS_WINDOWS

from msl.equipment.config import Config
from msl.equipment.connection_pyvisa import ConnectionPyVISA
from msl.equipment.record_types import EquipmentRecord, ConnectionRecord

from test_connection_socket import echo_server_tcp, get_available_port


pyvisa_skipif = pytest.mark.skipif(not IS_WINDOWS, reason='pyvisa tests are for Windows only')


@pyvisa_skipif
def test_resource_manager():
    assert isinstance(ConnectionPyVISA.resource_manager(), pyvisa.ResourceManager)


@pyvisa_skipif
def test_pyclass():

    for backend in ('@ni', '@py'):

        Config.PyVISA_LIBRARY = backend

        for item in ('ASRL1', 'ASRL1::INSTR', 'COM1', 'LPT1', 'ASRL::/dev/prt/1', 'ASRLCOM1'):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.SerialInstrument

        for item in ('GPIB::2', 'GPIB::1::0::INSTR'):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.GPIBInstrument

        for item in ('GPIB2::INTFC', ):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.GPIBInterface

        for item in ('PXI::15::INSTR', 'PXI::CHASSIS1::SLOT3', 'PXI0::2-12.1::INSTR'):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.PXIInstrument

        for item in ('PXI0::MEMACC',):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.PXIMemory

        for item in ('TCPIP::dev.company.com::INSTR',):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.TCPIPInstrument

        for item in ('TCPIP0::1.2.3.4::999::SOCKET',):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.TCPIPSocket

        for item in ('USB::0x1234::125::A22-5::INSTR',):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.USBInstrument

        for item in ('USB::0x5678::0x33::SN999::1::RAW',):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.USBRaw

        for item in ('VXI::1::BACKPLANE',):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.VXIBackplane

        for item in ('VXI::MEMACC',):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.VXIMemory

        for item in ('VXI0::1::INSTR', 'VXI0::SERVANT'):
            record = EquipmentRecord(connection=ConnectionRecord(address=item))
            assert ConnectionPyVISA.resource_class(record) == pyvisa.resources.VXIInstrument


@pyvisa_skipif
def test_timeout_and_termination():
    address = '127.0.0.1'
    port = get_available_port()
    term = b'xyz'

    t = threading.Thread(target=echo_server_tcp, args=(address, port, term))
    t.start()

    time.sleep(0.1)  # allow some time for the echo server to start

    record = EquipmentRecord(
        connection=ConnectionRecord(
            address='TCPIP::{}::{}::SOCKET'.format(address, port),
            backend='PyVISA',
            properties={'termination': term, 'timeout': 10}
        )
    )

    dev = record.connect()

    assert dev.timeout == 10000  # 10 seconds gets converted to 10000 ms
    assert dev.timeout == dev.resource.timeout
    assert dev.write_termination == term.decode()
    assert dev.write_termination == dev.resource.write_termination
    assert dev.read_termination == term.decode()
    assert dev.read_termination == dev.resource.read_termination

    dev.timeout = 1234
    dev.write_termination = 'hello'
    dev.read_termination = 'goodbye'
    assert dev.timeout == 1234
    assert dev.timeout == dev.resource.timeout
    assert dev.write_termination == 'hello'
    assert dev.write_termination == dev.resource.write_termination
    assert dev.read_termination == 'goodbye'
    assert dev.read_termination == dev.resource.read_termination

    del dev.timeout
    dev.write_termination = None
    dev.read_termination = None
    assert math.isinf(dev.timeout)
    assert dev.timeout == dev.resource.timeout
    assert dev.write_termination is None
    assert dev.resource.write_termination is None
    assert dev.read_termination is None
    assert dev.resource.read_termination is None

    dev.timeout = 5000
    dev.write_termination = term.decode()
    dev.read_termination = term.decode()
    assert dev.timeout == 5000
    assert dev.timeout == dev.resource.timeout
    assert dev.write_termination == term.decode()
    assert dev.write_termination == dev.resource.write_termination
    assert dev.read_termination == term.decode()
    assert dev.read_termination == dev.resource.read_termination

    dev.timeout = None
    assert math.isinf(dev.timeout)
    assert dev.timeout == dev.resource.timeout

    assert dev.query('*IDN?') == '*IDN?'

    dev.write('SHUTDOWN')
    dev.disconnect()
