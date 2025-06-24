#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Fake Data Generator Module
-----------------------
Generates fake data for signup tasks.
"""

import random
import string
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class FakeDataGenerator:
    """Generates fake data for signup tasks."""
    
    def __init__(self):
        """Initialize fake data generator."""
        # First names
        self.first_names = [
            "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph", "Thomas", "Charles",
            "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan", "Jessica", "Sarah", "Karen",
            "Christopher", "Daniel", "Matthew", "Anthony", "Mark", "Donald", "Steven", "Paul", "Andrew", "Joshua",
            "Michelle", "Amanda", "Kimberly", "Melissa", "Stephanie", "Laura", "Rebecca", "Sharon", "Cynthia", "Kathleen"
        ]
        
        # Last names
        self.last_names = [
            "Smith", "Johnson", "Williams", "Jones", "Brown", "Davis", "Miller", "Wilson", "Moore", "Taylor",
            "Anderson", "Thomas", "Jackson", "White", "Harris", "Martin", "Thompson", "Garcia", "Martinez", "Robinson",
            "Clark", "Rodriguez", "Lewis", "Lee", "Walker", "Hall", "Allen", "Young", "Hernandez", "King",
            "Wright", "Lopez", "Hill", "Scott", "Green", "Adams", "Baker", "Gonzalez", "Nelson", "Carter"
        ]
        
        # Domains for username generation
        self.domains = [
            "example.com", "mail.com", "testmail.com", "fakemail.org", "mailinator.com",
            "tempmail.net", "fakeinbox.com", "mailnesia.com", "mailcatch.com", "yopmail.com"
        ]
        
        # Cities
        self.cities = [
            "New York", "Los Angeles", "Chicago", "Houston", "Phoenix", "Philadelphia", "San Antonio", "San Diego",
            "Dallas", "San Jose", "Austin", "Jacksonville", "Fort Worth", "Columbus", "San Francisco", "Charlotte",
            "Indianapolis", "Seattle", "Denver", "Washington", "Boston", "El Paso", "Nashville", "Detroit", "Portland"
        ]
        
        # States
        self.states = [
            "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware", "Florida",
            "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky", "Louisiana", "Maine",
            "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi", "Missouri", "Montana", "Nebraska",
            "Nevada", "New Hampshire", "New Jersey", "New Mexico", "New York", "North Carolina", "North Dakota", "Ohio",
            "Oklahoma", "Oregon", "Pennsylvania", "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas",
            "Utah", "Vermont", "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
        ]
        
        # State abbreviations
        self.state_abbrs = [
            "AL", "AK", "AZ", "AR", "CA", "CO", "CT", "DE", "FL", "GA", "HI", "ID", "IL", "IN", "IA", "KS", "KY", "LA",
            "ME", "MD", "MA", "MI", "MN", "MS", "MO", "MT", "NE", "NV", "NH", "NJ", "NM", "NY", "NC", "ND", "OH", "OK",
            "OR", "PA", "RI", "SC", "SD", "TN", "TX", "UT", "VT", "VA", "WA", "WV", "WI", "WY"
        ]
        
        # Countries
        self.countries = [
            "United States", "Canada", "United Kingdom", "Australia", "Germany", "France", "Italy", "Spain", "Japan",
            "South Korea", "Brazil", "Mexico", "Argentina", "Netherlands", "Sweden", "Norway", "Denmark", "Finland",
            "Switzerland", "Austria", "Belgium", "Ireland", "New Zealand", "Singapore", "Malaysia"
        ]
        
        # Street names
        self.street_names = [
            "Main", "Park", "Oak", "Pine", "Maple", "Cedar", "Elm", "Washington", "Lake", "Hill",
            "First", "Second", "Third", "Fourth", "Fifth", "Sixth", "Seventh", "Eighth", "Ninth", "Tenth",
            "Spring", "Summer", "Autumn", "Winter", "River", "Mountain", "Valley", "Forest", "Meadow", "Garden"
        ]
        
        # Street types
        self.street_types = [
            "Street", "Avenue", "Boulevard", "Drive", "Lane", "Road", "Place", "Court", "Circle", "Way"
        ]
    
    def generate_first_name(self) -> str:
        """
        Generate a random first name.
        
        Returns:
            str: Random first name
        """
        return random.choice(self.first_names)
    
    def generate_last_name(self) -> str:
        """
        Generate a random last name.
        
        Returns:
            str: Random last name
        """
        return random.choice(self.last_names)
    
    def generate_username(self) -> str:
        """
        Generate a random username.
        
        Returns:
            str: Random username
        """
        # Choose a base for the username
        first_name = self.generate_first_name().lower()
        last_name = self.generate_last_name().lower()
        
        # Choose a username format
        username_format = random.choice([
            "{first}",
            "{first}{last}",
            "{first}.{last}",
            "{first}_{last}",
            "{first}{num}",
            "{first}.{last}{num}",
            "{first}_{last}{num}",
            "{first[0]}{last}",
            "{first[0]}.{last}",
            "{first[0]}_{last}"
        ])
        
        # Generate a random number
        num = random.randint(1, 9999)
        
        # Format username
        username = username_format.format(
            first=first_name,
            last=last_name,
            first_initial=first_name[0],
            last_initial=last_name[0],
            num=num
        )
        
        # Ensure username is not too long
        if len(username) > 20:
            username = username[:20]
        
        return username
    
    def generate_email(self) -> str:
        """
        Generate a random email address.
        
        Returns:
            str: Random email address
        """
        username = self.generate_username()
        domain = random.choice(self.domains)
        
        return f"{username}@{domain}"
    
    def generate_password(self, length: int = 12) -> str:
        """
        Generate a random password.
        
        Args:
            length: Password length
        
        Returns:
            str: Random password
        """
        # Define character sets
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase
        digits = string.digits
        special = "!@#$%^&*()-_=+[]{}|;:,.<>?"
        
        # Ensure at least one character from each set
        password = [
            random.choice(lowercase),
            random.choice(uppercase),
            random.choice(digits),
            random.choice(special)
        ]
        
        # Fill the rest of the password
        for _ in range(length - 4):
            password.append(random.choice(lowercase + uppercase + digits + special))
        
        # Shuffle password
        random.shuffle(password)
        
        return "".join(password)
    
    def generate_phone(self) -> str:
        """
        Generate a random US phone number.
        
        Returns:
            str: Random phone number
        """
        # Generate area code (avoid codes starting with 0 or 1)
        area_code = random.randint(200, 999)
        
        # Generate exchange code (avoid codes starting with 0 or 1)
        exchange_code = random.randint(200, 999)
        
        # Generate line number
        line_number = random.randint(1000, 9999)
        
        return f"{area_code}-{exchange_code}-{line_number}"
    
    def generate_address(self) -> str:
        """
        Generate a random street address.
        
        Returns:
            str: Random street address
        """
        # Generate house number
        house_number = random.randint(1, 9999)
        
        # Generate street name
        street_name = random.choice(self.street_names)
        
        # Generate street type
        street_type = random.choice(self.street_types)
        
        return f"{house_number} {street_name} {street_type}"
    
    def generate_city(self) -> str:
        """
        Generate a random city.
        
        Returns:
            str: Random city
        """
        return random.choice(self.cities)
    
    def generate_state(self) -> str:
        """
        Generate a random state.
        
        Returns:
            str: Random state
        """
        return random.choice(self.states)
    
    def generate_state_abbr(self) -> str:
        """
        Generate a random state abbreviation.
        
        Returns:
            str: Random state abbreviation
        """
        return random.choice(self.state_abbrs)
    
    def generate_zip(self) -> str:
        """
        Generate a random ZIP code.
        
        Returns:
            str: Random ZIP code
        """
        return str(random.randint(10000, 99999))
    
    def generate_country(self) -> str:
        """
        Generate a random country.
        
        Returns:
            str: Random country
        """
        return random.choice(self.countries)
    
    def generate_birthday(self, min_age: int = 18, max_age: int = 65) -> str:
        """
        Generate a random birthday.
        
        Args:
            min_age: Minimum age
            max_age: Maximum age
        
        Returns:
            str: Random birthday in MM/DD/YYYY format
        """
        # Calculate date range
        today = datetime.now()
        min_date = today - timedelta(days=max_age * 365)
        max_date = today - timedelta(days=min_age * 365)
        
        # Generate random date
        days_range = (max_date - min_date).days
        random_days = random.randint(0, days_range)
        random_date = min_date + timedelta(days=random_days)
        
        return random_date.strftime("%m/%d/%Y")
    
    def generate_gender(self) -> str:
        """
        Generate a random gender.
        
        Returns:
            str: Random gender
        """
        return random.choice(["Male", "Female"])
    
    def generate_person(self) -> Dict[str, str]:
        """
        Generate a complete fake person.
        
        Returns:
            Dict[str, str]: Fake person data
        """
        first_name = self.generate_first_name()
        last_name = self.generate_last_name()
        
        return {
            "first_name": first_name,
            "last_name": last_name,
            "full_name": f"{first_name} {last_name}",
            "username": self.generate_username(),
            "email": self.generate_email(),
            "password": self.generate_password(),
            "phone": self.generate_phone(),
            "address": self.generate_address(),
            "city": self.generate_city(),
            "state": self.generate_state(),
            "state_abbr": self.generate_state_abbr(),
            "zip": self.generate_zip(),
            "country": self.generate_country(),
            "birthday": self.generate_birthday(),
            "gender": self.generate_gender()
        }