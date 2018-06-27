# Copyright 2016 Google Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.appengine.ext import ndb
import webapp2
import json

class Boat(ndb.Model):
    id = ndb.StringProperty()
    name = ndb.StringProperty(required=True)
    type = ndb.StringProperty(required=True)
    length = ndb.IntegerProperty(required=True)
    at_sea = ndb.BooleanProperty(default=True)

class Slip(ndb.Model):
    id = ndb.StringProperty()
    number = ndb.IntegerProperty()
    current_boat = ndb.StringProperty(default=None)
    arrival_date = ndb.StringProperty(default=None)

class BoatHandler(webapp2.RequestHandler):
    def post(self):
        boat_data = json.loads(self.request.body)
        if len(boat_data) == 3 and "name" in boat_data and "type" in boat_data and "length" in boat_data:
            if type(boat_data['name']) == unicode and type(boat_data['type']) == unicode and type(boat_data['length']) == int:
                new_boat = Boat(name=boat_data['name'], type=boat_data['type'], length=boat_data['length'])
                new_boat.put()
                new_boat.id = '' + new_boat.key.urlsafe()
                new_boat.put()
                boat_dict = new_boat.to_dict()
                boat_dict['self'] = '/boat/' + new_boat.key.urlsafe()
                self.response.write(json.dumps(boat_dict))
                self.response.set_status(201)
            else:
                self.response.write("Invalid data types")
                self.response.set_status(400)
        else:
            self.response.write("Invalid body")
            self.response.set_status(400)

    def get(self, id=None):
        if id:
            query = Boat.query(Boat.id == id)
            boat = query.get()
            if boat != None:
                b_dict = boat.to_dict()
                b_dict['self'] = "/boat/" + id
                if boat.at_sea == False:
                    s_query = Slip.query(Slip.current_boat == ('silicon-perigee-191721.appspot.com/boat/' + boat.id))
                    slip = s_query.get()
                    if slip != None:
                        b_dict['slip'] = "/slip/" + slip.id
                self.response.write(json.dumps(b_dict))
            else:
                self.response.write("Invalid ID")
                self.response.set_status(400)
        else:
            boats = Boat.query().fetch()
            boat_list = []
            for b in boats:
                test_dict = b.to_dict()
                test_dict['self'] = '/boat/' + b.id
                if b.at_sea == False:
                    s_query = Slip.query(Slip.current_boat == ('silicon-perigee-191721.appspot.com/boat/' + b.id))
                    slip = s_query.get()
                    if slip != None:
                        test_dict['slip'] = "/slip/" + slip.id
                boat_list.append(test_dict)
            self.response.write(json.dumps(boat_list))
      
    def patch(self, id=None):
        if id:
            query = Boat.query(Boat.id == id)
            boat = query.get()
            if boat != None:
                boat_data = json.loads(self.request.body)
                if len(boat_data) == 3 and "name" in boat_data and "type" in boat_data and "length" in boat_data:
                    if type(boat_data['name']) == unicode and type(boat_data['type']) == unicode and type(boat_data['length']) == int:
                        boat.name = boat_data['name']
                        boat.type = boat_data['type']
                        boat.length = boat_data['length']
                        boat.put()
                        self.response.set_status(204)
                    else:
                        self.response.write("Invalid data types")
                        self.response.set_status(400)
                else:
                    self.response.write("Invalid request")
                    self.response.set_status(400)
            else:
                self.response.write("Invalid ID")
                self.response.set_status(400)

    def delete(self, id=None):
        if id:
            b_query = Boat.query(Boat.id == id)
            boat = b_query.get()
            if boat != None:
                if boat.at_sea == False:
                    query = Slip.query(Slip.current_boat == ('silicon-perigee-191721.appspot.com/boat/' + boat.id))
                    slip = query.get()
                    if slip != None:
                        slip.current_boat = None
                        slip.arrival_date = None
                        slip.put()
                self.response.set_status(204)
                boat.key.delete()
            else:
                self.response.write("Invalid ID")
                self.response.set_status(400)

    def put(self, id=None):
        if id:
            b_query = Boat.query(Boat.id == id)
            boat = b_query.get()
            if boat != None:
                slip_data = json.loads(self.request.body)
                if len(slip_data) == 2 and 'number' in slip_data and 'arrival_date' in slip_data:
                    if type(slip_data['number']) == int and type(slip_data['arrival_date']) == unicode:
                        query = Slip.query(Slip.number == slip_data['number'])
                        slip = query.get()
                        if slip != None:
                            if slip.current_boat == None:
                                slip.current_boat = 'silicon-perigee-191721.appspot.com/boat/' + boat.id
                                slip.arrival_date = slip_data['arrival_date']
                                boat.at_sea = False
                                slip.put()
                                boat.put()
                                self.response.set_status(204)
                            else:
                                self.response.set_status(403)
                        else:
                            self.response.write("Invalid Number")
                            self.response.set_status(400)
                    else:
                        self.response.write("Invalid data types")
                        self.response.set_status(400)
                else:
                    self.response.write("Invalid Request")
                    self.response.set_status(400)
            else:
                self.response.write("Invalid ID")
                self.response.set_status(400)

class SlipHandler(webapp2.RequestHandler):
    def post(self):
        slip_data = json.loads(self.request.body)
        if len(slip_data) == 1 and "number" in slip_data:
            if type(slip_data['number']) == int:
                query = Slip.query(Slip.number == slip_data['number'])
                slip = query.get()
                if slip == None:
                    new_slip = Slip(number=slip_data['number'])
                    new_slip.put()
                    new_slip.id = '' + new_slip.key.urlsafe()
                    new_slip.put()
                    slip_dict = new_slip.to_dict()
                    slip_dict['self'] = '/slip/' + new_slip.key.urlsafe()
                    self.response.set_status(201)
                    self.response.write(json.dumps(slip_dict))
                else:
                    self.response.write("Invalid number")
                    self.response.set_status(400)
            else:
                self.response.write("Invalid data types")
                self.response.set_status(400)
        else:
            self.response.write("Invalid request")
            self.response.set_status(400)

    def get(self, id=None):
        if id:
            query = Slip.query(Slip.id == id)
            slip = query.get()
            if slip != None: 
                s_dict = slip.to_dict()
                s_dict['self'] = '/slip/' + id
                self.response.write(json.dumps(s_dict))
            else:
                self.response.write("Invalid ID")
                self.response.set_status(400)
        else:
            slips = Slip.query().fetch()
            slip_list = []
            for s in slips:
                temp_dict = s.to_dict()
                temp_dict['self'] = '/slip/' + s.id
                slip_list.append(temp_dict)
            self.response.write(json.dumps(slip_list))

    def patch(self, id=None):
        if id:
            s_query = Slip.query(Slip.id == id)
            slip = s_query.get()
            if slip != None:
                slip_data = json.loads(self.request.body)
                if len(slip_data) == 1 and 'number' in slip_data:
                    if type(slip_data['number']) == int:
                        numberQuery = Slip.query(Slip.number == slip_data['number'])
                        repeatNumber = numberQuery.get()
                        if repeatNumber == None:
                            slip.number = slip_data['number']
                            slip.put()
                            self.response.set_status(204)
                        else:
                            self.response.write("Invalid Number")
                            self.response.set_status(400)
                    else:
                        self.response.write("Invalid data types")
                        self.response.set_status(400)
                else:
                    self.response.write("Invalid Request")
                    self.response.set_status(400)
            else:
                self.response.write("Invalid ID")
                self.response.set_status(400)

    def delete(self, id=None):
        if id:
            s_query = Slip.query(Slip.id == id)
            slip = s_query.get()
            if slip != None:
                if slip.current_boat != None:
                    boat_id = slip.current_boat.replace('silicon-perigee-191721.appspot.com/boat/', '')
                    query = Boat.query(Boat.id == boat_id)
                    boat = query.get()
                    if boat != None:
                        boat.at_sea = True
                        boat.put()
                self.response.set_status(204)
                slip.key.delete()
            else:
                self.response.write("Invalid ID")
                self.response.set_status(400)

    def put(self, id=None):
        if id:
            s_query = Slip.query(Slip.id == id)
            slip = s_query.get()
            if slip != None:
                boat_id = slip.current_boat.replace('silicon-perigee-191721.appspot.com/boat/', '') 
                query = Boat.query(Boat.id == boat_id)
                boat = query.get()
                if boat != None:
                    boat.at_sea = True
                    slip.current_boat = None
                    slip.arrival_date = None
                    boat.put()
                    slip.put()
                self.response.set_status(204)
            else:
                self.response.write("Invalid ID")
                self.response.set_status(400)

class MainPage(webapp2.RequestHandler):
    def get(self):
        self.response.headers['Content-Type'] = 'text/plain'
        self.response.write("Assignment 3 CS 496 REST API Main Page")

allowed_methods = webapp2.WSGIApplication.allowed_methods
new_allowed_methods = allowed_methods.union(('PATCH',))
webapp2.WSGIApplication.allowed_methods = new_allowed_methods
app = webapp2.WSGIApplication([
    ('/', MainPage),
    ('/boat', BoatHandler),
    ('/boat/(.*)', BoatHandler),
    ('/slip', SlipHandler),
    ('/slip/(.*)', SlipHandler)
], debug=True)
