#!/usr/bin/env python
# coding: utf-8

# In[1]:


import os
import time


# In[2]:


def task_sleep(idx):
    print(f"thread {idx} start pid: {os.getpid()}")
    time.sleep(2)
    print(f"thread {idx} done pid: {os.getpid()}")


# In[ ]:




