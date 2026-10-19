# models.py
from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import hashlib

Base = declarative_base()
engine = create_engine('sqlite:///hospital_new.db')
Session = sessionmaker(bind=engine)

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(128), nullable=False)
    full_name = Column(String(100), nullable=False)
    phone = Column(String(15))
    user_type = Column(String(20), nullable=False)  # 'admin' or 'patient'
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)

    def set_password(self, password):
        self.password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    def check_password(self, password):
        return self.password_hash == hashlib.sha256(password.encode()).hexdigest()

class DoctorSpecialization(Base):
    __tablename__ = 'doctor_specializations'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    description = Column(Text)
    
    # Relationship
    doctors = relationship("Doctor", back_populates="specialization")

class Doctor(Base):
    __tablename__ = 'doctors'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)
    email = Column(String(100), unique=True)
    phone = Column(String(15))
    specialization_id = Column(Integer, ForeignKey('doctor_specializations.id'))
    hospital_name = Column(String(200), nullable=False, default="AgnoHealth Hospital")
    license_number = Column(String(50), unique=True)
    years_experience = Column(Integer)
    consultation_fee = Column(Float)
    available = Column(Boolean, default=True)
    max_patients_per_day = Column(Integer, default=10)
    working_hours_start = Column(String(5), default="09:00")  # HH:MM format
    working_hours_end = Column(String(5), default="17:00")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    specialization = relationship("DoctorSpecialization", back_populates="doctors")
    appointments = relationship("Appointment", back_populates="doctor")

class BedType(Base):
    __tablename__ = 'bed_types'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)  # ICU, General, Private, Emergency
    description = Column(Text)
    daily_rate = Column(Float)
    
    # Relationship
    beds = relationship("Bed", back_populates="bed_type")

class Bed(Base):
    __tablename__ = 'beds'
    
    id = Column(Integer, primary_key=True)
    bed_number = Column(String(20), unique=True, nullable=False)
    bed_type_id = Column(Integer, ForeignKey('bed_types.id'))
    hospital_name = Column(String(200), nullable=False, default="AgnoHealth Hospital")
    floor_number = Column(Integer)
    room_number = Column(String(10))
    occupied = Column(Boolean, default=False)
    patient_name = Column(String(100))
    admission_date = Column(DateTime)
    expected_discharge_date = Column(DateTime)
    notes = Column(Text)
    
    # Relationship
    bed_type = relationship("BedType", back_populates="beds")

class Appointment(Base):
    __tablename__ = 'appointments'
    
    id = Column(Integer, primary_key=True)
    patient_email = Column(String(100), nullable=False)
    patient_name = Column(String(100))
    patient_phone = Column(String(15))
    doctor_id = Column(Integer, ForeignKey('doctors.id'))
    bed_id = Column(Integer, ForeignKey('beds.id'), nullable=True)
    appointment_time = Column(DateTime, nullable=False)
    appointment_type = Column(String(50), default='consultation')  # consultation, surgery, emergency
    symptoms = Column(Text)
    status = Column(String(20), default='scheduled')  # scheduled, completed, cancelled, in_progress
    diagnosis = Column(Text)
    prescription = Column(Text)
    follow_up_date = Column(DateTime)
    email_sent = Column(Boolean, default=False)
    reminder_sent = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    doctor = relationship("Doctor", back_populates="appointments")
    bed = relationship("Bed")

class EmailNotification(Base):
    __tablename__ = 'email_notifications'
    
    id = Column(Integer, primary_key=True)
    recipient_email = Column(String(100), nullable=False)
    subject = Column(String(200), nullable=False)
    body = Column(Text, nullable=False)
    notification_type = Column(String(50))  # appointment_confirmation, reminder, follow_up
    appointment_id = Column(Integer, ForeignKey('appointments.id'), nullable=True)
    scheduled_time = Column(DateTime)
    sent_time = Column(DateTime)
    status = Column(String(20), default='pending')  # pending, sent, failed
    retry_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)

class HospitalSettings(Base):
    __tablename__ = 'hospital_settings'
    
    id = Column(Integer, primary_key=True)
    hospital_name = Column(String(200), default='AgnoHealth Hospital')
    hospital_email = Column(String(100), default='info@agnohealth.com')
    hospital_phone = Column(String(15))
    hospital_address = Column(Text)
    smtp_server = Column(String(100), default='localhost')
    smtp_port = Column(Integer, default=1025)
    smtp_username = Column(String(100))
    smtp_password = Column(String(100))
    reminder_hours_before = Column(Integer, default=24)  # Send reminder 24 hours before appointment
    max_appointments_per_day = Column(Integer, default=50)
    emergency_contact = Column(String(15))

def init_database():
    Base.metadata.create_all(engine)
    
    session = Session()
    
    # Create default admin user
    admin_exists = session.query(User).filter_by(email='admin@agnohealth.com').first()
    if not admin_exists:
        admin = User(
            email='admin@agnohealth.com',
            full_name='Hospital Administrator',
            phone='+1234567890',
            user_type='admin'
        )
        admin.set_password('admin123')
        session.add(admin)
    
    # Create specializations
    specializations_data = [
        {'name': 'Cardiology', 'description': 'Heart and cardiovascular system'},
        {'name': 'Neurology', 'description': 'Brain and nervous system'},
        {'name': 'Orthopedics', 'description': 'Bones, joints, and muscles'},
        {'name': 'Pediatrics', 'description': 'Children healthcare'},
        {'name': 'Emergency Medicine', 'description': 'Emergency and critical care'},
        {'name': 'General Medicine', 'description': 'General healthcare and consultation'},
        {'name': 'Surgery', 'description': 'Surgical procedures'},
        {'name': 'Dermatology', 'description': 'Skin and related conditions'},
        {'name': 'ENT', 'description': 'Ear, Nose, and Throat'},
        {'name': 'Gynecology', 'description': 'Women health and reproductive system'},
        {'name': 'Pulmonology', 'description': 'Respiratory system and lung diseases'},
        {'name': 'Critical Care Medicine', 'description': 'Intensive care and life support'},
        {'name': 'Internal Medicine', 'description': 'Internal medicine and adult healthcare'},
        {'name': 'Family Medicine', 'description': 'Comprehensive family healthcare'},
        {'name': 'Pediatric Surgery', 'description': 'Surgical procedures for children'},
        {'name': 'Pediatric Cardiology', 'description': 'Heart conditions in children'},
        {'name': 'Trauma Surgery', 'description': 'Emergency surgical interventions'},
        {'name': 'Obstetrics', 'description': 'Pregnancy and childbirth care'},
        {'name': 'Maternal Medicine', 'description': 'Maternal health and pregnancy complications'},
        {'name': 'Anesthesiology', 'description': 'Anesthesia and pain management'},
        {'name': 'Radiology', 'description': 'Medical imaging and diagnostics'},
        {'name': 'Pathology', 'description': 'Disease diagnosis through tissue analysis'}
    ]
    
    for spec_data in specializations_data:
        exists = session.query(DoctorSpecialization).filter_by(name=spec_data['name']).first()
        if not exists:
            spec = DoctorSpecialization(**spec_data)
            session.add(spec)
    
    session.commit()
    
    # Create bed types
    bed_types_data = [
        {'name': 'ICU', 'description': 'Intensive Care Unit - Critical care beds', 'daily_rate': 500.0},
        {'name': 'General', 'description': 'General ward beds', 'daily_rate': 100.0},
        {'name': 'Private', 'description': 'Private rooms with premium facilities', 'daily_rate': 200.0},
        {'name': 'Emergency', 'description': 'Emergency department beds', 'daily_rate': 150.0}
    ]
    
    for bed_type_data in bed_types_data:
        exists = session.query(BedType).filter_by(name=bed_type_data['name']).first()
        if not exists:
            bed_type = BedType(**bed_type_data)
            session.add(bed_type)
    
    session.commit()
    
    # Create sample beds
    bed_types = session.query(BedType).all()
    bed_config = {
        'ICU': {'floors': [3, 4], 'beds_per_floor': 15},
        'General': {'floors': [1, 2], 'beds_per_floor': 25},
        'Private': {'floors': [5], 'beds_per_floor': 20},
        'Emergency': {'floors': [1], 'beds_per_floor': 12}
    }
    
    for bed_type in bed_types:
        if bed_type.name in bed_config:
            config = bed_config[bed_type.name]
            for floor in config['floors']:
                for bed_num in range(1, config['beds_per_floor'] + 1):
                    bed_number = f"{bed_type.name[0]}{floor}{bed_num:02d}"
                    room_number = f"{floor}{((bed_num-1)//2 + 1):02d}"
                    
                    exists = session.query(Bed).filter_by(bed_number=bed_number).first()
                    if not exists:
                        bed = Bed(
                            bed_number=bed_number,
                            bed_type_id=bed_type.id,
                            floor_number=floor,
                            room_number=room_number,
                            occupied=False
                        )
                        session.add(bed)
    
    session.commit()
    
    # Create sample doctors
    specializations = session.query(DoctorSpecialization).all()
    doctors_data = [
        {'name': 'Dr. Sarah Johnson', 'specialization': 'Cardiology', 'email': 'sarah.johnson@agnohealth.com', 'license': 'CARD001', 'experience': 15, 'fee': 200.0},
        {'name': 'Dr. Michael Chen', 'specialization': 'Neurology', 'email': 'michael.chen@agnohealth.com', 'license': 'NEURO001', 'experience': 12, 'fee': 250.0},
        {'name': 'Dr. Emily Davis', 'specialization': 'Pediatrics', 'email': 'emily.davis@agnohealth.com', 'license': 'PED001', 'experience': 8, 'fee': 150.0},
        {'name': 'Dr. Robert Wilson', 'specialization': 'Emergency Medicine', 'email': 'robert.wilson@agnohealth.com', 'license': 'EM001', 'experience': 10, 'fee': 180.0},
        {'name': 'Dr. Lisa Anderson', 'specialization': 'General Medicine', 'email': 'lisa.anderson@agnohealth.com', 'license': 'GM001', 'experience': 7, 'fee': 120.0},
        {'name': 'Dr. James Brown', 'specialization': 'Surgery', 'email': 'james.brown@agnohealth.com', 'license': 'SURG001', 'experience': 20, 'fee': 300.0},
        {'name': 'Dr. Maria Garcia', 'specialization': 'Gynecology', 'email': 'maria.garcia@agnohealth.com', 'license': 'GYN001', 'experience': 9, 'fee': 170.0},
        {'name': 'Dr. David Lee', 'specialization': 'Orthopedics', 'email': 'david.lee@agnohealth.com', 'license': 'ORTHO001', 'experience': 14, 'fee': 220.0},
        {'name': 'Dr. Amanda Wright', 'specialization': 'Pulmonology', 'email': 'amanda.wright@agnohealth.com', 'license': 'PULM001', 'experience': 11, 'fee': 190.0},
        {'name': 'Dr. Kevin Rodriguez', 'specialization': 'Critical Care Medicine', 'email': 'kevin.rodriguez@agnohealth.com', 'license': 'CCM001', 'experience': 13, 'fee': 280.0},
        {'name': 'Dr. Rachel Kim', 'specialization': 'Internal Medicine', 'email': 'rachel.kim@agnohealth.com', 'license': 'IM001', 'experience': 9, 'fee': 140.0},
        {'name': 'Dr. Thomas Martinez', 'specialization': 'Family Medicine', 'email': 'thomas.martinez@agnohealth.com', 'license': 'FM001', 'experience': 6, 'fee': 110.0},
        {'name': 'Dr. Jennifer Thompson', 'specialization': 'Pediatric Surgery', 'email': 'jennifer.thompson@agnohealth.com', 'license': 'PSURG001', 'experience': 16, 'fee': 320.0},
        {'name': 'Dr. Daniel Park', 'specialization': 'Trauma Surgery', 'email': 'daniel.park@agnohealth.com', 'license': 'TSURG001', 'experience': 18, 'fee': 350.0},
        {'name': 'Dr. Nicole White', 'specialization': 'Obstetrics', 'email': 'nicole.white@agnohealth.com', 'license': 'OBS001', 'experience': 12, 'fee': 200.0},
        {'name': 'Dr. Christopher Lee', 'specialization': 'Anesthesiology', 'email': 'christopher.lee@agnohealth.com', 'license': 'ANES001', 'experience': 15, 'fee': 240.0}
    ]
    
    for doctor_data in doctors_data:
        exists = session.query(Doctor).filter_by(email=doctor_data['email']).first()
        if not exists:
            specialization = next((s for s in specializations if s.name == doctor_data['specialization']), None)
            if specialization:
                doctor = Doctor(
                    name=doctor_data['name'],
                    email=doctor_data['email'],
                    phone=f"+1{hash(doctor_data['name']) % 9000000000 + 1000000000}",
                    specialization_id=specialization.id,
                    license_number=doctor_data['license'],
                    years_experience=doctor_data['experience'],
                    consultation_fee=doctor_data['fee'],
                    available=True
                )
                session.add(doctor)
    
    # Create hospital settings
    settings_exists = session.query(HospitalSettings).first()
    if not settings_exists:
        settings = HospitalSettings()
        session.add(settings)
    
    session.commit()
    session.close()
    
    print("Enhanced database initialized with comprehensive data!")

if __name__ == "__main__":
    init_database()
