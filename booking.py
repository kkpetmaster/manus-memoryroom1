from flask import Blueprint, request, jsonify
from datetime import datetime, date
from src.models.booking import db, Booking, Customer, Pet, Service, Staff
import json

booking_bp = Blueprint('booking', __name__)

@booking_bp.route('/bookings', methods=['GET'])
def get_bookings():
    """예약 목록 조회"""
    try:
        # 쿼리 파라미터 처리
        date_param = request.args.get('date')
        staff_param = request.args.get('staff')
        service_param = request.args.get('service')
        search_param = request.args.get('search')
        
        query = Booking.query
        
        # 날짜 필터
        if date_param:
            try:
                filter_date = datetime.strptime(date_param, '%Y-%m-%d').date()
                query = query.filter(Booking.date == filter_date)
            except ValueError:
                return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400
        
        # 직원 필터
        if staff_param and staff_param != 'all':
            staff = Staff.query.filter_by(name=staff_param).first()
            if staff:
                query = query.filter(Booking.staff_id == staff.id)
        
        # 서비스 필터
        if service_param and service_param != 'all':
            service = Service.query.filter_by(name=service_param).first()
            if service:
                query = query.filter(Booking.service_id == service.id)
        
        # 검색 필터 (고객명 또는 반려동물명)
        if search_param:
            query = query.join(Customer).join(Pet, Booking.pet_id == Pet.id, isouter=True).filter(
                db.or_(
                    Customer.name.contains(search_param),
                    Pet.name.contains(search_param)
                )
            )
        
        bookings = query.order_by(Booking.date, Booking.time).all()
        return jsonify([booking.to_dict() for booking in bookings])
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings', methods=['POST'])
def create_booking():
    """새 예약 생성"""
    try:
        data = request.get_json()
        
        # 필수 필드 검증
        required_fields = ['customerName', 'customerPhone', 'petName', 'serviceType', 'date', 'time', 'staff']
        for field in required_fields:
            if field not in data or not data[field]:
                return jsonify({'error': f'Missing required field: {field}'}), 400
        
        # 고객 찾기 또는 생성
        customer = Customer.query.filter_by(phone=data['customerPhone']).first()
        if not customer:
            customer = Customer(
                name=data['customerName'],
                phone=data['customerPhone'],
                email=data.get('customerEmail', ''),
                address=data.get('customerAddress', '')
            )
            db.session.add(customer)
            db.session.flush()  # ID 생성을 위해
        
        # 반려동물 찾기 또는 생성
        pet = Pet.query.filter_by(name=data['petName'], customer_id=customer.id).first()
        if not pet:
            pet = Pet(
                name=data['petName'],
                breed=data.get('petBreed', ''),
                customer_id=customer.id,
                notes=data.get('petNotes', '')
            )
            db.session.add(pet)
            db.session.flush()
        
        # 서비스 찾기
        service = Service.query.filter_by(name=data['serviceType']).first()
        if not service:
            return jsonify({'error': f'Service not found: {data["serviceType"]}'}), 400
        
        # 직원 찾기
        staff = Staff.query.filter_by(name=data['staff']).first()
        if not staff:
            return jsonify({'error': f'Staff not found: {data["staff"]}'}), 400
        
        # 예약 생성
        booking_date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        booking = Booking(
            customer_id=customer.id,
            pet_id=pet.id,
            service_id=service.id,
            staff_id=staff.id,
            date=booking_date,
            time=data['time'],
            duration=service.duration,
            price=service.base_price,
            status='confirmed',
            notes=data.get('notes', '')
        )
        
        db.session.add(booking)
        db.session.commit()
        
        return jsonify(booking.to_dict()), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings/<int:booking_id>', methods=['PUT'])
def update_booking(booking_id):
    """예약 수정"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        data = request.get_json()
        
        # 고객 정보 업데이트
        if 'customerName' in data:
            booking.customer.name = data['customerName']
        if 'customerPhone' in data:
            booking.customer.phone = data['customerPhone']
        
        # 반려동물 정보 업데이트
        if 'petName' in data:
            booking.pet.name = data['petName']
        if 'petBreed' in data:
            booking.pet.breed = data['petBreed']
        
        # 예약 정보 업데이트
        if 'date' in data:
            booking.date = datetime.strptime(data['date'], '%Y-%m-%d').date()
        if 'time' in data:
            booking.time = data['time']
        if 'serviceType' in data:
            service = Service.query.filter_by(name=data['serviceType']).first()
            if service:
                booking.service_id = service.id
                booking.duration = service.duration
                booking.price = service.base_price
        if 'staff' in data:
            staff = Staff.query.filter_by(name=data['staff']).first()
            if staff:
                booking.staff_id = staff.id
        if 'notes' in data:
            booking.notes = data['notes']
        if 'status' in data:
            booking.status = data['status']
        
        booking.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify(booking.to_dict())
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/bookings/<int:booking_id>', methods=['DELETE'])
def delete_booking(booking_id):
    """예약 삭제"""
    try:
        booking = Booking.query.get_or_404(booking_id)
        db.session.delete(booking)
        db.session.commit()
        
        return jsonify({'message': 'Booking deleted successfully'})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/customers', methods=['GET'])
def get_customers():
    """고객 목록 조회"""
    try:
        customers = Customer.query.order_by(Customer.name).all()
        return jsonify([customer.to_dict() for customer in customers])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/services', methods=['GET'])
def get_services():
    """서비스 목록 조회"""
    try:
        services = Service.query.filter_by(is_active=True).order_by(Service.name).all()
        return jsonify([service.to_dict() for service in services])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/staff', methods=['GET'])
def get_staff():
    """직원 목록 조회"""
    try:
        staff_list = Staff.query.filter_by(is_active=True).order_by(Staff.name).all()
        return jsonify([staff.to_dict() for staff in staff_list])
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@booking_bp.route('/stats/daily', methods=['GET'])
def get_daily_stats():
    """일일 통계 조회"""
    try:
        date_param = request.args.get('date', datetime.now().strftime('%Y-%m-%d'))
        filter_date = datetime.strptime(date_param, '%Y-%m-%d').date()
        
        bookings = Booking.query.filter(Booking.date == filter_date).all()
        
        total_bookings = len(bookings)
        confirmed_bookings = len([b for b in bookings if b.status == 'confirmed'])
        pending_bookings = len([b for b in bookings if b.status == 'pending'])
        completed_bookings = len([b for b in bookings if b.status == 'completed'])
        total_revenue = sum(booking.price or 0 for booking in bookings if booking.status in ['confirmed', 'completed'])
        
        return jsonify({
            'date': date_param,
            'total_bookings': total_bookings,
            'confirmed_bookings': confirmed_bookings,
            'pending_bookings': pending_bookings,
            'completed_bookings': completed_bookings,
            'total_revenue': total_revenue
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

