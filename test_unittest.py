import unittest
from . import app, db
from .models import Movie, User
from .commands import initdb, forge


class WatchlistTestCase(unittest.TestCase):
    def setUp(self):
        app.config.update(
                TESTING = True,
                SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
                )
        db.create_all()
        user = User(name='test', username='test')
        user.generate_password('123')
        movie = Movie(title='Test Movie Title', year='2019')
        db.session.add_all([user, movie])
        db.session.commit()

        self.client = app.test_client() # 创建测试客户端
        self.runner = app.test_cli_runner() # 创建测试命令运行器

    def tearDown(self):
        db.session.remove() # 清除数据库会话
        db.drop_all() # 删除数据库表

    def test_app_exist(self):
        self.assertIsNotNone(app)

    def test_app_is_testing(self):
        self.assertTrue(app.config['TESTING'])

    # 测试404页面
    def test_404_page(self):
        response = self.client.get('/nothing')
        data = response.get_data(as_text=True)
        self.assertIn('Page Not Found', data)
        self.assertIn('Go Back', data)
        self.assertEqual(response.status_code, 404)

    # 测试主页
    def test_main_page(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertIn('test\'s Watchlist', data)
        self.assertIn('Test Movie Title', data)
        self.assertEqual(response.status_code, 200)

    # 辅助方法，用于登入用户
    def login(self):
        self.client.post('/login', data=dict(
            username='test',
            password='123'), follow_redirects=True)

    # 测试创建条目
    def test_create_item(self):
        self.login()

        # 测试创建条目操作
        response = self.client.post('/', data=dict(
            title='New Movie',
            year='2019'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item Created', data)

    # 测试创建条目操作，但电影标题为空
        response = self.client.post('/', data=dict(
            title="",
            year='2019'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid Input', data)

    # 测试创建条目操作，但是年份为空
        response = self.client.post('/', data=dict(
            title="new movie",
            year=''), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Invalid Input', data)

    # 测试更新条目
        response = self.client.post('/movie/edit/1', data=dict(
            title="New Movie Title",
            year='2019'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item Changed', data)

    # 测试更新条目，但是电影标题为空
        response = self.client.post('/movie/edit/1', data=dict(
            title="",
            year='2019'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertNotIn('Item updated', data)
        self.assertIn('Invalid Input', data)

    # 测试删除条目
    def test_delete_item(self):
        self.login()
        response = self.client.post('/movie/delete/1', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Item deleted', data)
        self.assertNotIn('Test Movie Title', data)

    # 测试登录保护
    def test_login_protect(self):
        response = self.client.get('/')
        data = response.get_data(as_text=True)
        self.assertNotIn('Logout', data)
        self.assertNotIn('setting', data)
        self.assertNotIn('Delete', data)
        self.assertNotIn('edit', data)

    # 测试登录
    def test_login(self):
        response = self.client.post('/login', data=dict(
            username='test',
            password='123'), follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Login Success', data)
        self.assertIn('Logout', data)

    # 测试登出
    def test_logout(self):
        self.login()

        response = self.client.get('/logout', follow_redirects=True)
        data = response.get_data(as_text=True)
        self.assertIn('Good Bye', data)

    # 测试命令
    # 测试虚拟数据
    def test_forge_command(self):
        result = self.runner.invoke(forge)
        self.assertIn('Done', result.output)
        self.assertNotEqual(Movie.query.count(), 0)

    # 测试初始化数据库
    def test_initdb_command(self):
        result = self.runner.invoke(initdb)
        self.assertIn('Initialized database', result.output)


if __name__ == "__main__":
    unittest.main()
