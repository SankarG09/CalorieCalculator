import os, tempfile, unittest
from app import create_app
class CalculatorTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(); self.app=create_app({'TESTING':True,'DATABASE':os.path.join(self.tmp.name,'test.db'),'SECRET_KEY':'test-key'}); self.client=self.app.test_client(); self.token=self.client.get('/api/session').json['csrf']
    def tearDown(self): self.tmp.cleanup()
    def post(self,path,data): return self.client.post(path,json=data,headers={'X-CSRF-Token':self.token})
    def test_calculation_and_validation(self):
        r=self.post('/api/calculate',{'age':30,'height_cm':170,'weight_kg':65,'sex':'female','activity':'moderate','goal':'maintain'}); self.assertEqual(r.status_code,200); self.assertEqual(r.json['bmr'],1402); self.assertEqual(r.json['maintenance'],2172)
        self.assertEqual(self.post('/api/calculate',{'age':9}).status_code,400)
    def test_diary_total_delete_and_goal(self):
        self.assertEqual(self.post('/api/entries',{'food':'Oats','serving':'40 g','calories':152,'protein':5}).status_code,201)
        self.assertEqual(self.client.get('/api/entries').json['total'],152)
        self.assertEqual(self.post('/api/goal',{'target':2000}).json['target'],2000)
        entry=self.client.get('/api/entries').json['entries'][0]['id']; self.assertEqual(self.client.delete(f'/api/entries/{entry}',headers={'X-CSRF-Token':self.token}).status_code,200)
        self.assertEqual(self.client.get('/api/entries').json['total'],0)
    def test_csrf_and_bad_entry(self):
        self.assertEqual(self.client.post('/api/goal',json={'target':2000}).status_code,403)
        self.assertEqual(self.post('/api/entries',{'food':'','serving':'x','calories':-2}).status_code,400)
    def test_food_catalog_and_health(self):
        self.assertGreaterEqual(len(self.client.get('/api/foods').json),5); self.assertEqual(self.client.get('/health').json['status'],'healthy')
if __name__=='__main__': unittest.main()
