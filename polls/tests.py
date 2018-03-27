# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import datetime
from django.utils import timezone
from django.test import TestCase
from django.urls import reverse
from .models import Question

class QuestionModelTests(TestCase):
    def test_was_published_recently_with_future_question(self):
        # returns False for questions whose pub_date is set in the future
        time = timezone.now() + datetime.timedelta(days=30)
        future_question = Question(pub_date=time)
        self.assertIs(future_question.was_published_recently(), False)

    def test_was_published_recently_with_old_question(self):
        #returns false for questions whose pub_date is older than one day
        time = timezone.now() - datetime.timedelta(days=1, seconds=1)
        old_question = Question(pub_date=time)
        self.assertIs(old_question.was_published_recently(), False)

    def test_was_published_recently_with_recent_question(self):
        #returns True for questions whose pub_date is within the last day
        time = timezone.now() - datetime.timedelta(hours=23, minutes=59, seconds=59)
        recent_question = Question(pub_date=time)
        self.assertIs(recent_question.was_published_recently(), True)

    def create_question(question_text, days):
        #create a question with 'question_text' and published the given number of 'days' offset to now (- for previous questions, + for future)
        time = timezone.now() + datetime.timedelta(days=days)
        return Question.objects.create(question_text=question_text, pub_date=time)

    class QuestionIndexViewTests(TestCase):
        def test_no_questions(self):
            #if no questions, display msg
            res = self.client.get(reverse('polls:index'))
            self.assertEqual(res.status_code, 200)
            self.assertContains(res, "No polls available")
            self.assertQuerysetEqual(res.context['latest_question_list'], [])

        def test_past_question(self):
            #previous questions displayed on index page
            create_question(question_text="Past question.", days=-30)
            res = self.client.get(reverse('polls:index'))
            self.assertQuerysetEqual(res.context['latest_question_list'], ['<Question: Past question.>'])

        def test_future_question(self):
            #ensure questions scheduled for future are not displayed on index
            create_question(question_text="Future question.", days=30)
            res = self.client.get(reverse('polls:index'))
            self.assertContains(res, "No polls available")
            self.assertQuerysetEqual(res.context['latest_question_list'], [])

        def test_future_question_and_past_question(self):
            #if both scheduled and past questions exist, only display past questions
            create_question(question_text="Past question", days=-30)
            create_question(question_text="Future Question", days=30)
            res = self.client.get(reverse('polls:index'))
            self.assertQuerysetEqual(res.context['latest_question_list'], ['<Question: Past question.>'])

        def test_two_past_questions(self):
            #index page can display more than one question
            create_question(question_text="Past question 1", days=-30)
            create_question(question_text="Past question 2", days=-5)
            res = self.client.get(reverse('polls:index'))
            self.assertQuerysetEqual(res.context['latest_question_list'], ['<Question: Past question 2.>', '<Question: Past question 1.>'])
    
    class QuestionDetailViewTests(TestCase):
        def test_future_question(self):
            #detail view of a question scheduled for the future returns 404
            future_question = create_question(question_text="future question.", days=5)
            url = reverse('polls:detail', args=(future_question.id,))
            res = self.client.get(url)
            self.assertEqual(res.status_code, 404)

        def test_past_question(self):
            #detail view of past question displays the question's text
            past_question = create_question(question_text='Past Question.', days=-5)
            url = reverse('polls:detail', args=(past_question.id,))
            res = self.client.get(url)
            self.assertContains(res, past_question.question_text)