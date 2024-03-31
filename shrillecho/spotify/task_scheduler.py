

import asyncio
import math
import time
from typing import Callable, List, Type

from annotated_types import T


class TaskScheduler:

    def __init__(self):
        self.task_limit = 10
        self.active_task_count = 0
        self.tasks = []

    def load_task(self, task_func: Callable, *args):
        self.tasks.append((task_func, args))

    def load_tasks(self, tasks):
        self.tasks.extend(tasks)

    async def load_task_batch(self):
        current_batch = []
        for task_func, args in self.tasks[:self.task_limit]:
            current_batch.append(task_func(*args))
        return current_batch

    async def execute_tasks(self, unpack=True, batch_size=None):
        if batch_size:
            self.task_limit = batch_size
            
        all_results = []
        tasks_to_rerun = []

        while self.tasks:
            print(f'tasks to complete: {len(self.tasks)}')
            current_batch = []
            for task_func, args in self.tasks[:self.task_limit]:
                current_batch.append(task_func(*args))
        
            results = await asyncio.gather(*current_batch, return_exceptions=True)
          
            for (task_func, args), result in zip(self.tasks[:self.task_limit], results):
                if isinstance(result, Exception):
                
                    tasks_to_rerun.append((task_func, args))
                else:
                    all_results.append(result)

            self.tasks = self.tasks[self.task_limit:] + tasks_to_rerun
            tasks_to_rerun = []

        if unpack:
            unpacked = []
            for item in all_results:
                if isinstance(item, list):
                    for sub_item in item:
                        unpacked.append(sub_item)
                elif hasattr(item, 'items'):
                    for sub_item in item.items:
                        if hasattr(sub_item, 'track'):
                            unpacked.append(sub_item.track)
                        else:
                            unpacked.append(sub_item)
            return unpacked
        
        return all_results
        
            


        

    

