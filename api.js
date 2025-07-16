// API 서비스 모듈
const API_BASE_URL = 'http://localhost:5000/api';

class ApiService {
  async request(endpoint, options = {}) {
    const url = `${API_BASE_URL}${endpoint}`;
    const config = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    try {
      const response = await fetch(url, config);
      
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      
      return await response.json();
    } catch (error) {
      console.error('API request failed:', error);
      throw error;
    }
  }

  // 예약 관련 API
  async getBookings(params = {}) {
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/bookings?${queryString}` : '/bookings';
    return this.request(endpoint);
  }

  async createBooking(bookingData) {
    return this.request('/bookings', {
      method: 'POST',
      body: JSON.stringify(bookingData),
    });
  }

  async updateBooking(bookingId, bookingData) {
    return this.request(`/bookings/${bookingId}`, {
      method: 'PUT',
      body: JSON.stringify(bookingData),
    });
  }

  async deleteBooking(bookingId) {
    return this.request(`/bookings/${bookingId}`, {
      method: 'DELETE',
    });
  }

  // 고객 관련 API
  async getCustomers() {
    return this.request('/customers');
  }

  // 서비스 관련 API
  async getServices() {
    return this.request('/services');
  }

  // 직원 관련 API
  async getStaff() {
    return this.request('/staff');
  }

  // 통계 관련 API
  async getDailyStats(date) {
    const params = date ? { date } : {};
    const queryString = new URLSearchParams(params).toString();
    const endpoint = queryString ? `/stats/daily?${queryString}` : '/stats/daily';
    return this.request(endpoint);
  }
}

export default new ApiService();

