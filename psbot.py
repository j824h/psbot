import psutil
import argparse

import asyncio
import schedule

import actions.gnome

import logging
logging.basicConfig(level=logging.INFO)
logging.raiseExceptions = False


async def check_found(pid):
    try:
        psutil.Process(pid)
        return True
    except psutil.NoSuchProcess:
        return False
    

async def psbot(pid, name):
    found = await check_found(pid)
    if not found:
        raise SystemExit("The process is not found")

    # Scheduled checks
    async def check_and_update():
        nonlocal found
        found = await check_found(pid)

    def create_task():
        global task
        task = asyncio.create_task(check_and_update())

    task = asyncio.create_task(asyncio.sleep(0))
    schedule.every().minutes.do(create_task).tag("default")

    while found:
        schedule.run_pending()
        await asyncio.gather(
            task,
            asyncio.sleep(0.5)
        )
    
    logging.info("Taking actions for the terminated process")
    await actions.gnome.alert_terminated(pid, name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('pid', type=int)
    parser.add_argument('--name', default="", help='nickname for the process')
    args = parser.parse_args()

    asyncio.run(psbot(args.pid, args.name))
