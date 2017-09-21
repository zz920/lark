import time
import requests
from multiprocessing import Process, Manager


class DownloadTask(Process):

    def __init__(self, task_pool, file_pool, url_validator=None):
        super().__init__()

        # initial state to accept download task
        self.isValid = True
        self.url_validator = url_validator
        self.task_pool = task_pool
        self.file_pool = file_pool

        # ensure the task is ended after the main process exit
        self.daemon = True

    def run(self):
        # this is not truely run the process,
        # it means the process starts to listen to the manager to assign a task.
        # the processing is start listening -> get a task -> download -> put the
        # result back -> keep listening.
        # maintence the process is to reduce the cost of established a new one.
        while True:
            new_task = self.task_pool.get()
            url, header, chunk_descriptor = new_task
            if not verifyUrl(url, self.url_validator):
                continue    
            
            chunk = self.download(url, header)
            self.file_pool.put((chunk, chunk_descriptor))

    def download(self, url, header):
        return requests.get(url, headers=header).content
        

class FileRecorder(Process):
    
    def __init__(self, file_pool):
        super().__init__()  
        
        # used to manage when to close the file
        self.file_dict = {}

        self.file_pool = file_pool
        # ensure the task is ended after the main process exit
        self.daemon = True

    def _make_exist(self, file_loc):
        if file_loc not in self.file_dict:
            self.file_dict[file_loc] = (open(file_loc, 'wb'), 0)

    def get_file_obj(self, file_loc):
        self._make_exist(file_loc)
        return self.file_dict[file_loc][0]

    def get_file_size(self, file_loc):
        self._make_exist(file_loc)
        return self.file_dict[file_loc][1]

    def append_file_size(self, file_loc, offset):
        self._make_exist(file_loc)
        f_obj, size = self.file_dict[file_loc]
        self.file_dict[file_loc] = (f_obj, size+offset)

    def remove_file_obj(self, file_loc):
        del self.file_dict[file_loc]

    def run(self):
        # write the chunk to file and make sure the integrity of the file,
        # especially in the case that the task process is terminated in
        # accident, it should record which chunk is written and reload those not
        # downloaded part.
        while True:
             
            chunk, chunk_descriptor = self.file_pool.get()
            file_descriptor, rang = chunk_descriptor

            start, end = rang
            file_loc, total_size = file_descriptor
            try:
                f_obj = self.get_file_obj(file_loc)
                f_obj.seek(start)
                f_obj.write(chunk)
            except:
                raise ValueError("file written failed.")
            finally:
                self.append_file_size(file_loc, end - start + 1)
                #print("finished writing. %d" % self.get_file_size(file_loc))
 
                # written finished
                if self.get_file_size(file_loc) >= total_size:
                    self.get_file_obj(file_loc).close()
                    self.remove_file_obj(file_loc) 
                
            # TODO: record the chunk has been written.
                
class TaskManager():

    # ensure there is only one TaskManger in this world.
    __instance__ = None

    def __new__(cls, *args, **kwds):
        if TaskManager.__instance__ is None:
            TaskManager.__instance__ = object.__new__(cls, *args, **kwds)
        return TaskManager.__instance__

    def __init__(self, max_proc_num=4, url_validator=None):

        self.max_proc_num = max_proc_num
        self.chunkSize = 2097152
        self.task_pool = Manager().Queue(2 * max_proc_num)
        self.file_pool = Manager().Queue(2 * max_proc_num)

        self.url_validator = url_validator 
        self._createTasks() 
    
    @property
    def hasTask(self):
        return (not self.task_pool.empty()) and (not self.file_pool.empty()) 
    
    def _createTasks(self):

        task_list = [
            DownloadTask(self.task_pool, self.file_pool, self.url_validator) 
            for _ in range(self.max_proc_num)]
        self.task_list = task_list
        self.recorder = FileRecorder(self.file_pool)
        
    def start(self):

        for task in self.task_list:
            # task start to listen for a download task
            task.start()

        self.recorder.start()


    def add_task(self, url, file_location):
        
        if not verifyUrl(url, self.url_validator):
            raise ValueError("url is illegal.")

        request = requests.head(url)

        if 'Content-Length' not in request.headers:
            raise ValueError("url is not a download link.")

        size = int(request.headers['Content-Length'])
        # TODO check size is legal

        file_des = (file_location, size)

        # TODO use a process to feed task_pool, rather than main proc.
        for ran in splitChunk(size, self.chunkSize):
            self.task_pool.put((url, makeupHeader(ran), (file_des, ran)))
    
    def stop(self):

        while self.hasTask:
            time.sleep(0.5)
        self.terminate()


    def terminate(self):
        
        for task in self.task_list:
            task.terminate()

        self.recorder.terminate()
        #delete the instance or not?
        TaskManager.__instance__ = None

def makeupHeader(ran):
    return {'Range':'bytes=%s-%s' % ran, 'Accept-Encoding':'*'}

    
def splitChunk(size, limit):
    delta = 0
    while delta < size:
        if delta + limit < size:
            yield(delta, delta + limit-1)
        else:
            yield(delta, size-1)
        delta += limit
        

def verifyUrl(url, validator=None):
    if validator is None or not callable(validator):
        return True

    return validator(url)
