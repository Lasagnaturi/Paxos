#!/usr/bin/env python3
import sys
import socket
import struct
from proposer import Proposer
from client import client
from learner import Learner
from acceptor import Acceptor
from connection import mcast_receiver, mcast_sender


def parse_cfg(cfgpath):
  cfg = {}
  with open(cfgpath, 'r') as cfgfile:
    for line in cfgfile:
      (role, host, port) = line.split()
      cfg[role] = (host, int(port))
  return cfg




if __name__ == '__main__':
  cfgpath = sys.argv[1]
  config = parse_cfg(cfgpath)
  role = sys.argv[2]
  id = int(sys.argv[3])
  if role == 'acceptor':
    rolefunc = Acceptor.acceptor
  elif role == 'proposer':
    rolefunc = Proposer.proposer
  elif role == 'learner':
    rolefunc = Learner.learner
  elif role == 'client':
    rolefunc = client
  rolefunc(config, id)
