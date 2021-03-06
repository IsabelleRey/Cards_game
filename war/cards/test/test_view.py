from django.http import HttpResponseRedirect
from django.test import TestCase
from mock import Mock, patch
from cards.models import Player, WarGame
from cards.utils import create_deck
from django.core.urlresolvers import reverse


class ViewTestCase(TestCase):
    def setUp(self):
        create_deck()

    # def test_home_page(self):
    #     response = self.client.get(reverse('home'))
    #     self.assertIn('<p>Suit: spade, Rank: two</p>', response.content)
    #     self.assertEqual(response.context['cards'].count(), 52)

    def test_FAQ_page(self):
        response = self.client.get(reverse('faq'))
        self.assertIn('<p>Q: Can I win real money on this website?</p>', response.content)

    def test_filters_page(self):
        response = self.client.get(reverse('filters'))
        self.assertIn('Capitalized Suit:', response.content)
        self.assertIn('TWO', response.content)
        self.assertIn('THREE', response.content)
        self.assertIn('FOUR', response.content)
        self.assertIn('FIVE', response.content)
        self.assertIn('SIX', response.content)
        self.assertIn('SEVEN', response.content)
        self.assertIn('EIGHT', response.content)
        self.assertEqual(response.context['cards'].count(), 52)

    def test_register_page(self):
        username = 'new-user'
        data = {
            'username': username,
            'email': 'test@test.com',
            'password1': 'test',
            'password2': 'test'
        }
        response = self.client.post(reverse('register'), data)

        # Check this user was created in the database
        self.assertTrue(Player.objects.filter(username=username).exists())

        # Check it's a redirect to the profile page
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('profile')))

    def test_login_page(self):
        Player.objects.create_user(username='username', email='test@test.com', password='test')
        data = {
            'username': 'username',
            'password': 'test'
        }
        response = self.client.post(reverse('login'), data)
        self.assertIsInstance(response, HttpResponseRedirect)
        self.assertTrue(response.get('location').endswith(reverse('profile')))

    def create_war_game(self, user, result=WarGame.LOSS):
        WarGame.objects.create(result=result, player=user)

    def test_profile_page(self):
        # Create user and log them in
        password = 'passsword'
        user = Player.objects.create_user(username='test-user', email='test@test.com', password=password)
        self.client.login(username=user.username, password=password)

        # Set up some war game entries
        self.create_war_game(user)
        self.create_war_game(user, WarGame.WIN)

        # Make the url call and check the html and games queryset length
        response = self.client.get(reverse('profile'))
        self.assertInHTML('<p>Your email address is {}</p>'.format(user.email), response.content)
        self.assertEqual(len(response.context['games']), 2)

    # def test_war_page(self):
    #     war = WarGame.objects.create(result='result', player='user')
    #     pass

    @patch('cards.utils.requests')
    def test_home_page(self, mock_requests):
        mock_comic = {
        'num': 1433,
        'year': "2014",
        'safe_title': "Lightsaber",
        'alt': "A long time in the future, in a galaxy far, far, away.",
        'transcript': "An unusual gamma-ray burst originating from somewhere across the universe.",
        'img': "http://imgs.xkcd.com/comics/lightsaber.png",
        'title': "Lightsaber",
        }
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = mock_comic
        mock_requests.get.return_value = mock_response
        response = self.client.get(reverse('home'))
        self.assertIn('<h3>{} - {}</h3>'.format(mock_comic['safe_title'], mock_comic['year']),
                      response.content)
        self.assertIn('<img alt="{}" src="{}">'.format(mock_comic['alt'], mock_comic['img']),
                      response.content)
        self.assertIn('<p>{}</p>'.format(mock_comic['transcript']), response.content)
