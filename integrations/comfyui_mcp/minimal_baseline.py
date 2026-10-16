"""Independent minimal durable stop + explicit history baseline.

Shares ONLY stdio transport/ID parsing, not DurableClient persistence or binding.
Raw request/config is stored locally: do not publish the database.
"""
import json
import os
import sqlite3

from bridge import BridgeError, StdioMCP, job_id


class MinimalClient:
    def __init__(self, database, command, endpoint, *, mode=None, timeout=30):
        self.command = list(command)
        self.environment = dict(os.environ)
        self.timeout = timeout
        self.context = {'endpoint':endpoint, 'command':self.command,
                        'environment':{k:v for k,v in self.environment.items()
                                       if k.startswith(('COMFY','MCP_'))}}
        self.db = sqlite3.connect(database,timeout=10)
        self.db.execute('PRAGMA synchronous=FULL')
        self.db.execute('CREATE TABLE IF NOT EXISTS operations (run TEXT PRIMARY KEY, binding TEXT, job TEXT)')
        self.db.commit()

    def close(self):
        self.db.close()

    def _call(self, name, arguments):
        child = StdioMCP(self.command,timeout=self.timeout,env=self.environment)
        try:
            return child.call(name,arguments)
        finally:
            child.close()

    def submit(self, run_id, key, workflow):
        binding = json.dumps({'key':key,'workflow':workflow,'context':self.context},
                             sort_keys=True,allow_nan=False)
        self.db.execute('BEGIN IMMEDIATE')
        try:
            old = self.db.execute('SELECT binding,job FROM operations WHERE run=?',(run_id,)).fetchone()
            if old:
                if old[0] != binding:
                    raise BridgeError('Request binding conflict')
            else:
                self.db.execute('INSERT INTO operations VALUES (?,?,NULL)',(run_id,binding))
            self.db.commit()
        except BaseException:
            self.db.rollback()
            raise
        if old:
            if old[1] is None:
                raise BridgeError('Submission outcome unknown; no automatic resubmission')
            return {'state':'known_job','prompt_id':old[1]}
        result = self._call('enqueue_workflow',{'action':'enqueue','workflow':workflow})
        pid = job_id(result)
        self.db.execute('UPDATE operations SET job=? WHERE run=?',(pid,run_id))
        self.db.commit()
        return {'state':'known_job','prompt_id':pid}

    def inspect(self, run_id):
        row = self.db.execute('SELECT job FROM operations WHERE run=?',(run_id,)).fetchone()
        if row is None:
            raise BridgeError('Unknown run')
        return {'state':'unknown' if row[0] is None else 'known_job','prompt_id':row[0]}

    def read_history(self, run_id):
        binding, pid = self.db.execute('SELECT binding,job FROM operations WHERE run=?',(run_id,)).fetchone()
        if json.loads(binding)['context'] != self.context:
            raise BridgeError('Recovery context conflict')
        if pid is None:
            raise BridgeError('No retained prompt_id')
        return self._call('get_history',{'action':'list','prompt_id':pid})
