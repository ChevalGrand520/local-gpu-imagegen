import copy
import unittest
from scripts.research.cpu_evidence_contract import audit, constructed_checks


class CpuEvidenceContractTests(unittest.TestCase):
    def test_constructed_expectations(self):
        for case in constructed_checks():
            with self.subTest(case=case['name']):
                self.assertTrue(case['passed'],case['actual'])

    def test_posts_do_not_prove_execution(self):
        r=copy.deepcopy(constructed_checks()[0]['record'])
        ev=r['snapshots'][0]['events']
        for e in ev[:3]:e['kind']='post_received'
        self.assertEqual(audit(r)['executions'],0)

    def test_two_executions_under_same_job_are_distinct(self):
        r=copy.deepcopy(constructed_checks()[0]['record'])
        original=r['snapshots'][0]['events']; events=copy.deepcopy(original[:3])
        for event in original[1:3]:
            e=copy.deepcopy(event);e['execution_id']='execution-2';events.append(e)
        events.append(copy.deepcopy(original[-1]))
        for i,e in enumerate(events,1):e.update(seq=i,event_id=f'e{i}',monotonic_ns=i)
        r['final_seq']=6;r['snapshots']=[dict(first_seq=1,last_seq=6,events=events)]
        self.assertEqual(audit(r)['executions'],2)
        events[4]['kind']='observation_gap'
        self.assertEqual(audit(r)['state'],'unknown')

    def test_unbound_terminal_is_unknown(self):
        r=copy.deepcopy(constructed_checks()[0]['record'])
        r['snapshots'][0]['events'][2]['job_id']='other-job'
        self.assertEqual(audit(r)['state'],'unknown')


if __name__=='__main__':unittest.main()
