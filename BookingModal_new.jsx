import { useState, useEffect } from 'react'
import { X } from 'lucide-react'

export default function BookingModal({ booking, services, staff, onSave, onClose }) {
  const [formData, setFormData] = useState({
    customerName: '',
    customerPhone: '',
    customerEmail: '',
    customerAddress: '',
    petName: '',
    petBreed: '',
    serviceType: '',
    date: new Date().toISOString().split('T')[0],
    time: '09:00',
    staff: '',
    notes: ''
  })

  useEffect(() => {
    if (booking) {
      setFormData({
        customerName: booking.customer_name || '',
        customerPhone: booking.customer_phone || '',
        customerEmail: booking.customer_email || '',
        customerAddress: booking.customer_address || '',
        petName: booking.pet_name || '',
        petBreed: booking.pet_breed || '',
        serviceType: booking.service_type || '',
        date: booking.date || new Date().toISOString().split('T')[0],
        time: booking.time || '09:00',
        staff: booking.staff || '',
        notes: booking.notes || ''
      })
    }
  }, [booking])

  const handleSubmit = (e) => {
    e.preventDefault()
    onSave(formData)
  }

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData(prev => ({
      ...prev,
      [name]: value
    }))
  }

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg p-6 w-full max-w-md max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold">
            {booking ? '예약 수정' : '신규 예약'}
          </h2>
          <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          {/* 고객 정보 */}
          <div>
            <h3 className="font-medium text-gray-700 mb-2">고객 정보</h3>
            <div className="space-y-3">
              <input
                type="text"
                name="customerName"
                placeholder="고객명"
                value={formData.customerName}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <input
                type="tel"
                name="customerPhone"
                placeholder="연락처"
                value={formData.customerPhone}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <input
                type="email"
                name="customerEmail"
                placeholder="이메일 (선택사항)"
                value={formData.customerEmail}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
              <input
                type="text"
                name="customerAddress"
                placeholder="주소 (선택사항)"
                value={formData.customerAddress}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* 반려동물 정보 */}
          <div>
            <h3 className="font-medium text-gray-700 mb-2">반려동물 정보</h3>
            <div className="space-y-3">
              <input
                type="text"
                name="petName"
                placeholder="반려동물 이름"
                value={formData.petName}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />
              <input
                type="text"
                name="petBreed"
                placeholder="견종"
                value={formData.petBreed}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* 예약 정보 */}
          <div>
            <h3 className="font-medium text-gray-700 mb-2">예약 정보</h3>
            <div className="space-y-3">
              <select
                name="serviceType"
                value={formData.serviceType}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">서비스 선택</option>
                {services.map(service => (
                  <option key={service.id} value={service.name}>
                    {service.name} ({service.duration}분, {service.base_price.toLocaleString()}원)
                  </option>
                ))}
              </select>

              <input
                type="date"
                name="date"
                value={formData.date}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />

              <input
                type="time"
                name="time"
                value={formData.time}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              />

              <select
                name="staff"
                value={formData.staff}
                onChange={handleChange}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                required
              >
                <option value="">담당자 선택</option>
                {staff.map(s => (
                  <option key={s.id} value={s.name}>
                    {s.name} ({s.position})
                  </option>
                ))}
              </select>

              <textarea
                name="notes"
                placeholder="특이사항"
                value={formData.notes}
                onChange={handleChange}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              />
            </div>
          </div>

          <div className="flex space-x-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="flex-1 px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              취소
            </button>
            <button
              type="submit"
              className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              {booking ? '수정' : '저장'}
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}

