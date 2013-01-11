import unittest
import urllib
import ittybitty
import threading




class testapplication(ittybitty.ittybitty_server):

    @ittybitty.get("/")
    def index(self, request):
        return "index"





class BasicTestCase(unittest.TestCase):


    def test_1_start_up(self):
        self.server = testapplication(host="10.50.159.204", port=7890)
        self.server.start()
        response = urllib.urlopen("http://10.50.159.204:7890/html-ref")
        self.assertEqual(response.getcode(), 200)
        self.server.stop()


#    def test_2_webserice_response(self):
#        response = urllib.urlopen("http://127.0.0.1:8080")
#        self.assetTrue(response.read())

if __name__ == "__main__":
    unittest.main()
        
        
        
        
        
        
