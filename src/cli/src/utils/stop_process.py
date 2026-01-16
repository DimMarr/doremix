import psutil


def stop_process(pid: int):
    if psutil.pid_exists(pid):
        process = psutil.Process(pid)
        children = process.children(recursive=True)

        # SIGTERM
        process.terminate()
        for child in children:
            child.terminate()

        # Wait for 3 secondes and SIGKILL alive process
        gone, alive = psutil.wait_procs([process] + children, timeout=3)
        for p in alive:
            p.kill()
    else:
        return "PID doesn't exists."
