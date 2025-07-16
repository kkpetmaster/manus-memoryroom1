import { useState, useEffect } from 'react'
import { Calendar, Search, Plus, ChevronLeft, ChevronRight, Users, Settings } from 'lucide-react'
import BookingModal from './components/BookingModal'
import BookingDetailModal from './components/BookingDetailModal'
import ApiService from './services/api'
import './App.css'

function App() {
  const [currentDate, setCurrentDate] = useState(new Date())
  const [selectedDate, setSelectedDate] = useState(new Date())
  const [bookings, setBookings] = useState([])
  const [filteredBookings, setFilteredBookings] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [selectedStaff, setSelectedStaff] = useState('all')
  const [selectedService, setSelectedService] = useState('all')
  const [showBookingModal, setShowBookingModal] = useState(false)
  const [showDetailModal, setShowDetailModal] = useState(false)
  const [selectedBooking, setSelectedBooking] = useState(null)
  const [editingBooking, setEditingBooking] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  
  // 기본 데이터
  const [services, setServices] = useState([])
  const [staff, setStaff] = useState([])
  const [dailyStats, setDailyStats] = useState({})

  // 데이터 로딩
  useEffect(() => {
    loadInitialData()
  }, [])

  // 날짜 변경 시 예약 데이터 다시 로딩
  useEffect(() => {
    if (services.length > 0 && staff.length > 0) {
      loadBookings()
    }
  }, [selectedDate, services, staff])

  // 검색 및 필터링
  useEffect(() => {
    filterBookings()
  }, [bookings, searchTerm, selectedStaff, selectedService])

  const loadInitialData = async () => {
    try {
      setLoading(true)
      const [servicesData, staffData] = await Promise.all([
        ApiService.getServices(),
        ApiService.getStaff()
      ])
      
      setServices(servicesData)
      setStaff(staffData)
      setError(null)
    } catch (err) {
      console.error('Failed to load initial data:', err)
      setError('데이터를 불러오는데 실패했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const loadBookings = async () => {
    try {
      const dateStr = selectedDate.toISOString().split('T')[0]
      const [bookingsData, statsData] = await Promise.all([
        ApiService.getBookings({ date: dateStr }),
        ApiService.getDailyStats(dateStr)
      ])
      
      setBookings(bookingsData)
      setDailyStats(statsData)
      setError(null)
    } catch (err) {
      console.error('Failed to load bookings:', err)
      setError('예약 데이터를 불러오는데 실패했습니다.')
    }
  }

  const filterBookings = () => {
    let filtered = [...bookings]

    if (searchTerm) {
      filtered = filtered.filter(booking => 
        booking.customer_name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
        booking.pet_name?.toLowerCase().includes(searchTerm.toLowerCase())
      )
    }

    if (selectedStaff !== 'all') {
      filtered = filtered.filter(booking => booking.staff === selectedStaff)
    }

    if (selectedService !== 'all') {
      filtered = filtered.filter(booking => booking.service_type === selectedService)
    }

    setFilteredBookings(filtered)
  }

  const handleSaveBooking = async (bookingData) => {
    try {
      if (editingBooking) {
        await ApiService.updateBooking(editingBooking.id, bookingData)
      } else {
        await ApiService.createBooking(bookingData)
      }
      
      await loadBookings() // 데이터 다시 로딩
      setShowBookingModal(false)
      setEditingBooking(null)
    } catch (err) {
      console.error('Failed to save booking:', err)
      alert('예약 저장에 실패했습니다.')
    }
  }

  const handleDeleteBooking = async (bookingId) => {
    if (window.confirm('정말로 이 예약을 삭제하시겠습니까?')) {
      try {
        await ApiService.deleteBooking(bookingId)
        await loadBookings() // 데이터 다시 로딩
        setShowDetailModal(false)
        setSelectedBooking(null)
      } catch (err) {
        console.error('Failed to delete booking:', err)
        alert('예약 삭제에 실패했습니다.')
      }
    }
  }

  const getServiceColor = (serviceType) => {
    const colors = {
      '미용': 'bg-blue-100 text-blue-800 border-blue-200',
      '목욕': 'bg-green-100 text-green-800 border-green-200',
      '네일': 'bg-purple-100 text-purple-800 border-purple-200',
      '귀청소': 'bg-pink-100 text-pink-800 border-pink-200',
      '부분미용': 'bg-yellow-100 text-yellow-800 border-yellow-200',
      '전체미용': 'bg-indigo-100 text-indigo-800 border-indigo-200'
    }
    return colors[serviceType] || 'bg-gray-100 text-gray-800 border-gray-200'
  }

  const generateTimeSlots = () => {
    const slots = []
    for (let hour = 8; hour <= 18; hour++) {
      slots.push(`${hour.toString().padStart(2, '0')}:00`)
    }
    return slots
  }

  const getBookingsForTimeSlot = (time) => {
    return filteredBookings.filter(booking => booking.time === time)
  }

  const formatDate = (date) => {
    return date.toLocaleDateString('ko-KR', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      weekday: 'long'
    })
  }

  const navigateDate = (direction) => {
    const newDate = new Date(selectedDate)
    newDate.setDate(newDate.getDate() + direction)
    setSelectedDate(newDate)
  }

  const openNewBookingModal = () => {
    setEditingBooking(null)
    setShowBookingModal(true)
  }

  const openEditBookingModal = (booking) => {
    setEditingBooking(booking)
    setShowBookingModal(true)
    setShowDetailModal(false)
  }

  const openBookingDetail = (booking) => {
    setSelectedBooking(booking)
    setShowDetailModal(true)
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">데이터를 불러오는 중...</p>
        </div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">{error}</p>
          <button 
            onClick={loadInitialData}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
          >
            다시 시도
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      {/* 사이드바 */}
      <div className="w-64 bg-white shadow-lg">
        <div className="p-6">
          <h1 className="text-xl font-bold text-gray-800 mb-8">애견샵 관리</h1>
          
          <nav className="space-y-2">
            <div className="flex items-center space-x-3 p-3 text-red-600 bg-red-50 rounded-lg">
              <span className="text-sm">📢</span>
              <span className="text-sm font-medium">새소식</span>
            </div>
            <div className="flex items-center space-x-3 p-3 text-gray-600 hover:bg-gray-50 rounded-lg cursor-pointer">
              <span className="text-sm">📋</span>
              <span className="text-sm">공지사항</span>
            </div>
            <div className="flex items-center space-x-3 p-3 text-blue-600 bg-blue-50 rounded-lg">
              <Calendar className="w-4 h-4" />
              <span className="text-sm font-medium">예약</span>
            </div>
            <div className="flex items-center space-x-3 p-3 text-gray-600 hover:bg-gray-50 rounded-lg cursor-pointer">
              <span className="text-sm">📨</span>
              <span className="text-sm">수신</span>
            </div>
            <div className="flex items-center space-x-3 p-3 text-gray-600 hover:bg-gray-50 rounded-lg cursor-pointer">
              <span className="text-sm">🌐</span>
              <span className="text-sm">온라인</span>
            </div>
            <div className="flex items-center space-x-3 p-3 text-gray-600 hover:bg-gray-50 rounded-lg cursor-pointer">
              <Users className="w-4 h-4" />
              <span className="text-sm">고객</span>
            </div>
            <div className="flex items-center space-x-3 p-3 text-gray-600 hover:bg-gray-50 rounded-lg cursor-pointer">
              <span className="text-sm">💬</span>
              <span className="text-sm">문자발송</span>
            </div>
            <div className="flex items-center space-x-3 p-3 text-gray-600 hover:bg-gray-50 rounded-lg cursor-pointer">
              <span className="text-sm">💳</span>
              <span className="text-sm">결제</span>
            </div>
            <div className="flex items-center space-x-3 p-3 text-gray-600 hover:bg-gray-50 rounded-lg cursor-pointer">
              <span className="text-sm">📊</span>
              <span className="text-sm">매출</span>
            </div>
            <div className="flex items-center space-x-3 p-3 text-gray-600 hover:bg-gray-50 rounded-lg cursor-pointer">
              <span className="text-sm">🔔</span>
              <span className="text-sm">알림장</span>
            </div>
          </nav>
        </div>

        {/* 미니 달력 */}
        <div className="p-6 border-t">
          <div className="text-sm font-medium text-gray-700 mb-3">
            {currentDate.getFullYear()}년 {currentDate.getMonth() + 1}월
          </div>
          <div className="grid grid-cols-7 gap-1 text-xs">
            {['일', '월', '화', '수', '목', '금', '토'].map(day => (
              <div key={day} className="text-center text-gray-500 p-1">{day}</div>
            ))}
            {Array.from({ length: 31 }, (_, i) => (
              <div 
                key={i + 1} 
                className={`text-center p-1 cursor-pointer rounded ${
                  selectedDate.getDate() === i + 1 
                    ? 'bg-blue-600 text-white' 
                    : 'hover:bg-gray-100'
                }`}
                onClick={() => {
                  const newDate = new Date(currentDate)
                  newDate.setDate(i + 1)
                  setSelectedDate(newDate)
                }}
              >
                {i + 1}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 메인 콘텐츠 */}
      <div className="flex-1 p-6">
        {/* 헤더 */}
        <div className="flex items-center justify-between mb-6">
          <div className="flex items-center space-x-4">
            <button 
              onClick={openNewBookingModal}
              className="flex items-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              <Plus className="w-4 h-4" />
              <span>신규 예약</span>
            </button>
            
            <div className="relative">
              <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
              <input
                type="text"
                placeholder="고객명, 반려동물명 검색..."
                className="pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
          </div>

          <div className="flex items-center space-x-4">
            <button 
              onClick={() => navigateDate(-1)}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <ChevronLeft className="w-5 h-5" />
            </button>
            
            <div className="text-lg font-semibold">
              {formatDate(selectedDate)}
            </div>
            
            <button 
              onClick={() => navigateDate(1)}
              className="p-2 hover:bg-gray-100 rounded-lg"
            >
              <ChevronRight className="w-5 h-5" />
            </button>

            <select 
              className="px-3 py-2 border border-gray-300 rounded-lg"
              value={selectedStaff}
              onChange={(e) => setSelectedStaff(e.target.value)}
            >
              <option value="all">전체 직원</option>
              {staff.map(s => (
                <option key={s.id} value={s.name}>{s.name}</option>
              ))}
            </select>

            <select 
              className="px-3 py-2 border border-gray-300 rounded-lg"
              value={selectedService}
              onChange={(e) => setSelectedService(e.target.value)}
            >
              <option value="all">전체 서비스</option>
              {services.map(s => (
                <option key={s.id} value={s.name}>{s.name}</option>
              ))}
            </select>

            <button className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700">
              미용
            </button>
            <button className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50">
              일간
            </button>
          </div>
        </div>

        {/* 스케줄러 */}
        <div className="bg-white rounded-lg shadow">
          <div className="grid grid-cols-4 border-b">
            <div className="p-4 font-medium text-gray-700">시간</div>
            <div className="p-4 font-medium text-gray-700">원장님</div>
            <div className="p-4 font-medium text-gray-700">실장님</div>
            <div className="p-4 font-medium text-gray-700">기타</div>
          </div>

          {generateTimeSlots().map(time => {
            const timeBookings = getBookingsForTimeSlot(time)
            return (
              <div key={time} className="grid grid-cols-4 border-b min-h-[80px]">
                <div className="p-4 bg-gray-50 font-medium text-gray-600">
                  {time}
                </div>
                
                {['원장님', '실장님', '기타'].map(staffName => {
                  const staffBookings = timeBookings.filter(booking => 
                    staffName === '기타' ? !['원장님', '실장님'].includes(booking.staff) : booking.staff === staffName
                  )
                  
                  return (
                    <div key={staffName} className="p-2">
                      {staffBookings.map(booking => (
                        <div
                          key={booking.id}
                          className={`p-2 rounded-lg border cursor-pointer mb-1 ${getServiceColor(booking.service_type)}`}
                          onClick={() => openBookingDetail(booking)}
                        >
                          <div className="font-medium text-sm">{booking.customer_name}</div>
                          <div className="text-xs">{booking.pet_name}</div>
                          <div className="text-xs">{booking.service_type}</div>
                        </div>
                      ))}
                    </div>
                  )
                })}
              </div>
            )
          })}
        </div>

        {/* 하단 통계 */}
        <div className="mt-6 grid grid-cols-4 gap-4">
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">오늘 예약</div>
            <div className="text-2xl font-bold text-blue-600">{dailyStats.total_bookings || 0}건</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">확정 예약</div>
            <div className="text-2xl font-bold text-green-600">{dailyStats.confirmed_bookings || 0}건</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">대기 예약</div>
            <div className="text-2xl font-bold text-yellow-600">{dailyStats.pending_bookings || 0}건</div>
          </div>
          <div className="bg-white p-4 rounded-lg shadow">
            <div className="text-sm text-gray-600">예상 매출</div>
            <div className="text-2xl font-bold text-purple-600">
              {(dailyStats.total_revenue || 0).toLocaleString()}원
            </div>
          </div>
        </div>
      </div>

      {/* 모달들 */}
      {showBookingModal && (
        <BookingModal
          booking={editingBooking}
          services={services}
          staff={staff}
          onSave={handleSaveBooking}
          onClose={() => {
            setShowBookingModal(false)
            setEditingBooking(null)
          }}
        />
      )}

      {showDetailModal && selectedBooking && (
        <BookingDetailModal
          booking={selectedBooking}
          onEdit={openEditBookingModal}
          onDelete={handleDeleteBooking}
          onClose={() => {
            setShowDetailModal(false)
            setSelectedBooking(null)
          }}
        />
      )}
    </div>
  )
}

export default App

