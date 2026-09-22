import re
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, model_validator


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=1, description="Analyst password")


class SignupRequest(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1, max_length=100, description="First name")
    second_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Second name")
    full_name: Optional[str] = Field(None, min_length=1, max_length=100)
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, description="Password with minimum 6 characters")
    confirm_password: Optional[str] = Field(None, description="Confirm password must match password")
    organization: Optional[str] = Field(None, max_length=150, description="Organization / Company")
    role: Optional[str] = Field("Security Analyst", description="Analyst role / clearance level")

    @model_validator(mode="after")
    def validate_signup(self):
        # Resolve full_name from first_name + second_name or provided full_name
        if self.first_name and self.second_name:
            resolved_name = f"{self.first_name.strip()} {self.second_name.strip()}"
        elif self.first_name:
            resolved_name = self.first_name.strip()
        else:
            resolved_name = (self.full_name or self.name or "").strip()

        if not resolved_name:
            raise ValueError("First Name and Second Name (or Full Name) are required.")
        self.full_name = resolved_name
        self.name = resolved_name

        # Password validation: minimum 8 characters, digit, and uppercase
        pwd = self.password
        if len(pwd) < 8:
            raise ValueError("Password must be at least 8 characters long.")
        if not re.search(r"\d", pwd):
            raise ValueError("Password must contain at least one numerical digit.")
        if not re.search(r"[A-Z]", pwd):
            raise ValueError("Password must contain at least one uppercase letter.")

        # Confirm password match if supplied
        if self.confirm_password is not None and self.confirm_password != self.password:
            raise ValueError("Passwords do not match.")

        return self


class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=6, description="Security password with minimum 6 characters")
    role: Optional[str] = Field("Security Analyst", description="Analyst role / clearance level")
    organization: Optional[str] = Field(None, max_length=150)


class UserProfileResponse(BaseModel):
    id: str
    first_name: Optional[str] = None
    second_name: Optional[str] = None
    full_name: Optional[str] = None
    name: Optional[str] = None
    email: str
    organization: Optional[str] = None
    role: Optional[str] = "Lead Security Analyst"
    is_active: Optional[bool] = True
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    last_login: Optional[str] = None

    @model_validator(mode="after")
    def populate_name_aliases(self):
        if not self.full_name and self.name:
            self.full_name = self.name
        if not self.name and self.full_name:
            self.name = self.full_name
        if not self.first_name and self.full_name:
            parts = self.full_name.split(' ', 1)
            self.first_name = parts[0]
            if len(parts) > 1 and not self.second_name:
                self.second_name = parts[1]
        return self


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfileResponse
    message: str = "Authentication successful"
