# User Authentication System

## Overview
The user authentication system allows users to create accounts, log in, and manage their sessions securely.

## Features
- User registration with email and password
- Login with email/password
- Password reset functionality
- Session management
- Account verification

## Registration Process
1. User provides email and password
2. System validates email format
3. System checks if email is already registered
4. If valid, account is created and verification email sent
5. User clicks verification link to activate account

## Login Process
1. User enters email and password
2. System validates credentials
3. If valid, session token is created
4. User is redirected to dashboard

## Security Requirements
- Passwords must be at least 8 characters
- Emails must be valid format
- Accounts must be verified before login
- Sessions expire after 24 hours of inactivity

## Error Scenarios
- Invalid email format
- Password too short
- Account already exists
- Wrong credentials
- Unverified account</content>
<parameter name="filePath">d:\college\PROJECTS\multimodal RAG\data\input\authentication_system.md