"""Manage only Wi-Fi lockdown; never print device identifiers or pairing material."""
import argparse
import asyncio
import json
from pymobiledevice3.lockdown import create_using_usbmux
from pymobiledevice3.usbmux import list_devices

async def main(mode):
    devices = await list_devices()
    counts = {kind: sum(d.connection_type == kind for d in devices) for kind in ('USB', 'Network')}
    print(json.dumps({'devices': counts}))
    kind = 'Network' if mode == 'network' else 'USB'
    candidates = [d for d in devices if d.connection_type == kind]
    if len(candidates) != 1:
        raise RuntimeError(f'Expected exactly one {kind} device; found {len(candidates)}')
    async with await create_using_usbmux(serial=candidates[0].serial, connection_type=kind, autopair=False) as phone:
        if not phone.paired:
            raise RuntimeError('Existing trust relationship is unavailable; no pairing was changed')
        before = await phone.get_enable_wifi_connections()
        if mode in ('enable', 'disable'):
            await phone.set_enable_wifi_connections(mode == 'enable')
        after = await phone.get_enable_wifi_connections()
        print(json.dumps({'transport':kind, 'trusted':True, 'wifiBefore':before, 'wifiAfter':after}))

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=['status', 'enable', 'disable', 'network'])
    args = parser.parse_args()
    try:
        asyncio.run(asyncio.wait_for(main(args.mode), timeout=30))
    except Exception as error:
        # Exception messages may contain device identifiers; keep diagnostics non-sensitive.
        print(json.dumps({'error':type(error).__name__}))
        raise SystemExit(1)
