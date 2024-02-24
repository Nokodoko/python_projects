#!/bin/env python3

from pydantic import BaseModel
from typing import List

class Rum(BaseModel):
    url: str
    redirect: bool

class APM_Monitor(BaseModel):
    tags: List[str]
    environment: str
    alert_recipients: List[str]

    @create.setter
    def create(name):
        file = '~/forest/terraform/variables.tf'



class FS_Service(BaseModel):
    service_name: str
    cloud_provider: str
    Rum: BaseModel
    APM_Monitor: BaseModel
