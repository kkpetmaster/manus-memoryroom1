import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime, date
import json
from src.models.booking import db, Customer, Pet, Service, Staff, Booking
from src.main import app

def init_sample_data():
    """샘플 데이터 초기화"""
    with app.app_context():
        # 기존 데이터 삭제 (개발용)
        db.drop_all()
        db.create_all()
        
        # 서비스 데이터 생성
        services = [
            Service(name='미용', duration=120, base_price=50000, description='기본 미용 서비스'),
            Service(name='목욕', duration=90, base_price=30000, description='목욕 및 드라이'),
            Service(name='네일', duration=30, base_price=15000, description='발톱 정리'),
            Service(name='귀청소', duration=20, base_price=10000, description='귀 청소 서비스'),
            Service(name='부분미용', duration=60, base_price=35000, description='얼굴, 발끝 등 부분 미용'),
            Service(name='전체미용', duration=180, base_price=80000, description='전체 미용 패키지')
        ]
        
        for service in services:
            db.session.add(service)
        
        # 직원 데이터 생성
        staff_list = [
            Staff(
                name='원장님',
                position='원장',
                specialties=json.dumps(['전체미용', '미용', '네일', '귀청소']),
                working_hours_start='09:00',
                working_hours_end='18:00',
                working_days=json.dumps(['월', '화', '수', '목', '금', '토'])
            ),
            Staff(
                name='실장님',
                position='실장',
                specialties=json.dumps(['목욕', '부분미용', '전체미용']),
                working_hours_start='09:00',
                working_hours_end='18:00',
                working_days=json.dumps(['월', '화', '수', '목', '금'])
            )
        ]
        
        for staff in staff_list:
            db.session.add(staff)
        
        db.session.commit()
        
        # 고객 및 반려동물 데이터 생성
        customers_data = [
            {
                'name': '김철수',
                'phone': '010-1234-5678',
                'email': 'kim@email.com',
                'address': '서울시 강남구 역삼동',
                'pets': [
                    {'name': '멍멍이', 'breed': '골든 리트리버', 'age': 3, 'weight': 25.0, 'notes': '활발하고 사람을 좋아함'}
                ]
            },
            {
                'name': '이영희',
                'phone': '010-2345-6789',
                'email': 'lee@email.com',
                'address': '서울시 서초구 서초동',
                'pets': [
                    {'name': '뽀삐', 'breed': '푸들', 'age': 2, 'weight': 8.0, 'notes': '피부가 예민함'}
                ]
            },
            {
                'name': '박민수',
                'phone': '010-3456-7890',
                'email': 'park@email.com',
                'address': '서울시 송파구 잠실동',
                'pets': [
                    {'name': '초코', 'breed': '시바견', 'age': 4, 'weight': 12.0, 'notes': '발톱 자르기를 싫어함'}
                ]
            },
            {
                'name': '정수진',
                'phone': '010-4567-8901',
                'email': 'jung@email.com',
                'address': '서울시 마포구 홍대입구',
                'pets': [
                    {'name': '루비', 'breed': '말티즈', 'age': 1, 'weight': 3.5, 'notes': '첫 방문이에요. 많이 무서워할 수 있어요.'}
                ]
            },
            {
                'name': '최동현',
                'phone': '010-5678-9012',
                'email': 'choi@email.com',
                'address': '서울시 영등포구 여의도동',
                'pets': [
                    {'name': '바둑이', 'breed': '믹스견', 'age': 5, 'weight': 15.0, 'notes': ''}
                ]
            }
        ]
        
        for customer_data in customers_data:
            customer = Customer(
                name=customer_data['name'],
                phone=customer_data['phone'],
                email=customer_data['email'],
                address=customer_data['address']
            )
            db.session.add(customer)
            db.session.flush()
            
            for pet_data in customer_data['pets']:
                pet = Pet(
                    name=pet_data['name'],
                    breed=pet_data['breed'],
                    age=pet_data['age'],
                    weight=pet_data['weight'],
                    notes=pet_data['notes'],
                    customer_id=customer.id
                )
                db.session.add(pet)
        
        db.session.commit()
        
        # 예약 데이터 생성
        bookings_data = [
            {
                'customer_phone': '010-1234-5678',
                'pet_name': '멍멍이',
                'service_name': '미용',
                'staff_name': '원장님',
                'date': '2025-07-14',
                'time': '10:00',
                'status': 'confirmed',
                'notes': '털이 많이 엉켜있어요. 조심스럽게 해주세요.'
            },
            {
                'customer_phone': '010-2345-6789',
                'pet_name': '뽀삐',
                'service_name': '목욕',
                'staff_name': '실장님',
                'date': '2025-07-14',
                'time': '14:00',
                'status': 'confirmed',
                'notes': '피부가 예민해요.'
            },
            {
                'customer_phone': '010-3456-7890',
                'pet_name': '초코',
                'service_name': '네일',
                'staff_name': '원장님',
                'date': '2025-07-14',
                'time': '11:00',
                'status': 'pending',
                'notes': '발톱 자르기를 싫어해요.'
            },
            {
                'customer_phone': '010-4567-8901',
                'pet_name': '루비',
                'service_name': '전체미용',
                'staff_name': '실장님',
                'date': '2025-07-14',
                'time': '09:00',
                'status': 'confirmed',
                'notes': '첫 방문이에요. 많이 무서워할 수 있어요.'
            },
            {
                'customer_phone': '010-5678-9012',
                'pet_name': '바둑이',
                'service_name': '목욕',
                'staff_name': '원장님',
                'date': '2025-07-14',
                'time': '16:00',
                'status': 'confirmed',
                'notes': ''
            }
        ]
        
        for booking_data in bookings_data:
            customer = Customer.query.filter_by(phone=booking_data['customer_phone']).first()
            pet = Pet.query.filter_by(name=booking_data['pet_name'], customer_id=customer.id).first()
            service = Service.query.filter_by(name=booking_data['service_name']).first()
            staff = Staff.query.filter_by(name=booking_data['staff_name']).first()
            
            booking = Booking(
                customer_id=customer.id,
                pet_id=pet.id,
                service_id=service.id,
                staff_id=staff.id,
                date=datetime.strptime(booking_data['date'], '%Y-%m-%d').date(),
                time=booking_data['time'],
                duration=service.duration,
                price=service.base_price,
                status=booking_data['status'],
                notes=booking_data['notes']
            )
            db.session.add(booking)
        
        db.session.commit()
        print("샘플 데이터 초기화 완료!")

if __name__ == '__main__':
    init_sample_data()

