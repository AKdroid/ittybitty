import unittest
import urllib
import ittybitty
import threading




class testapplication(ittybitty.itty_server):

    @ittybitty.get("/")
    def index(self, request):
        return "index"



class BasicTestCase(unittest.TestCase):

    def setUp(self):
        self.ta = testapplication()
        self.ta.run_in_thread()

    def tearDown(self): 
        self.ta.stop()

    def test_1_webservice_running(self):
        response = urllib.urlopen("http://127.0.0.1:8080")
        self.assertEqual(response.getcode(), 200)


#    def test_2_webserice_response(self):
#        response = urllib.urlopen("http://127.0.0.1:8080")
#        self.assetTrue(response.read())

if __name__ == "__main__":
    unittest.main()
        
        
        
        
        
        
