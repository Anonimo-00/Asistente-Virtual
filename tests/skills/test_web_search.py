import unittest
from integrations.skills.web_search.web_search_skill import WebSearchSkill

class TestWebSearchSkill(unittest.TestCase):
    def setUp(self):
        self.skill = WebSearchSkill()

    def test_search(self):
        params = {
            "query": "Python programming tutorial",
            "num_results": 3
        }
        
        result = self.skill.execute(params)
        self.assertTrue('success' in result)
        self.assertTrue(result.get('success'))
        self.assertTrue('results' in result)
        self.assertGreater(len(result['results']), 0)
        
        # Verificar estructura de resultados
        first_result = result['results'][0]
        self.assertIn('title', first_result)
        self.assertIn('url', first_result)
        self.assertIn('snippet', first_result)
        self.assertIn('content', first_result)

    def test_invalid_search(self):
        params = {
            "query": "",
            "num_results": 1
        }
        
        result = self.skill.execute(params)
        self.assertIn('error', result)
        self.assertEqual(result['error'], "La consulta de búsqueda no puede estar vacía")

    def test_malformed_query(self):
        params = {
            "query": "   ",
            "num_results": 1
        }
        
        result = self.skill.execute(params)
        self.assertIn('error', result)

if __name__ == '__main__':
    unittest.main()
