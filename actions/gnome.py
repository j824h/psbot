import gi
gi.require_version('Notify', '0.7')

from gi.repository import Notify
Notify.init("KREP Alerts")

async def alert_terminated(pid="", name=""):
    if name == "":
        notification = Notify.Notification.new("Process terminated", f"PID: {pid}")
    else:
        notification = Notify.Notification.new("Process terminated", f"Process: {name}\nPID: {pid}" )
    notification.set_urgency(2)
    notification.show()