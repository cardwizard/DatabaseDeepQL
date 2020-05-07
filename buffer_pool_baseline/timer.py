class Time:
    def __init__(self, start_time: int = 0):
        self.time_step = start_time

    def increment(self):
        self.time_step += 1

    def now(self):
        return self.time_step

    def reset(self):
        self.time_step = 0

    def copy(self):
        t = Time(self.time_step)
        return t
