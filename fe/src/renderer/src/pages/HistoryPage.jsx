import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import Skeleton from 'react-loading-skeleton'
import 'react-loading-skeleton/dist/skeleton.css'
import bgDarkmode from '../assets/bg-darkmode.png'
import borderImage from '../assets/border/history.svg'
import backIcon from '../assets/back-Icon.svg'
import filterIcon from '../assets/filter-history-page.svg'

const BASE_URL = import.meta.env.VITE_BASE_URL
const ENDPOINT = '/v1/history-scan'

const HistoryPage = () => {
  const navigate = useNavigate()
  const [data, setData] = useState([])
  const [searchTerm, setSearchTerm] = useState('')
  const [currentPage, setCurrentPage] = useState(1)
  const [isLoading, setIsLoading] = useState(true)
  const [sortOrder, setSortOrder] = useState({
    number: true,
    lastScan: true,
    scanType: true,
    securityPercentage: true
  })
  const [itemsPerPage, setItemsPerPage] = useState(10)
  const [dropdownOpen, setDropdownOpen] = useState(false)

  // Fetch data dari API (respon berbentuk array)
  useEffect(() => {
    const fetchData = async () => {
      setIsLoading(true)
      try {
        const response = await fetch(`${BASE_URL}${ENDPOINT}`)
        const result = await response.json()
        if (Array.isArray(result)) {
          setData(result)
        } else {
          console.error('Respon tidak berbentuk array:', result)
        }
      } catch (error) {
        console.error('Error fetching data:', error)
      } finally {
        setIsLoading(false)
      }
    }
    fetchData()
  }, [])

  // Reset halaman ke 1 setiap kali searchTerm berubah
  useEffect(() => {
    setCurrentPage(1)
  }, [searchTerm])

  // Fungsi sorting yang umum untuk berbagai key
  const handleSort = (key) => {
    const isAsc = sortOrder[key]
    const sortedData = [...data].sort((a, b) => {
      switch (key) {
        case 'number':
          return isAsc ? a.no - b.no : b.no - a.no
        case 'lastScan':
          return isAsc
            ? new Date(b.last_scan) - new Date(a.last_scan)
            : new Date(a.last_scan) - new Date(b.last_scan)
        case 'scanType':
          return isAsc
            ? (a.scan_type?.localeCompare(b.scan_type) ?? 0)
            : (b.scan_type?.localeCompare(a.scan_type) ?? 0)
        case 'securityPercentage': {
          // Bungkus dalam blok untuk deklarasi lexical
          const aPercentage = parseFloat(a.security_percentage.replace('%', ''))
          const bPercentage = parseFloat(b.security_percentage.replace('%', ''))
          return isAsc ? aPercentage - bPercentage : bPercentage - aPercentage
        }
        default:
          return 0
      }
    })
    setData(sortedData)
    setSortOrder((prev) => ({ ...prev, [key]: !isAsc }))
  }

  // Fungsi untuk mengubah jumlah item per halaman
  const handleItemsPerPageChange = (number) => {
    setItemsPerPage(number)
    setDropdownOpen(false)
    setCurrentPage(1)
  }

  // Filter data berdasarkan pencarian
  const filteredData = data.filter((item) => {
    const lowerSearch = searchTerm.toLowerCase().trim()
    return (
      item.name?.toLowerCase().includes(lowerSearch) ||
      item.model?.toLowerCase().includes(lowerSearch) ||
      item.imei1?.toLowerCase().includes(lowerSearch) ||
      item.last_scan?.toLowerCase().includes(lowerSearch)
    )
  })

  // Tambahkan fungsi handleDetail
  const handleDetail = (item) => {
    // Misal scan_id: "Power51280003007_18022025_165044"
    const [serialNumber, ...timeParts] = item.scan_id.split('_')
    const timeStamp = timeParts.join('_')
    
    if (item.scan_type === 'full-scan') {
      navigate(`/history-detail/full-scan/${serialNumber}/${timeStamp}`)
    } else if (item.scan_type === 'fast-scan') {
      navigate(`/history-detail/fast-scan/${serialNumber}/${timeStamp}`)
    }
  }
  

  // Pagination
  const totalPages = Math.ceil(filteredData.length / itemsPerPage)
  const currentData = filteredData.slice(
    (currentPage - 1) * itemsPerPage,
    currentPage * itemsPerPage
  )

  const handlePageChange = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page)
    }
  }

  return (
    <div
      className="h-screen w-screen flex flex-col  items-center relative text-white font-aldrich"
      style={{
        backgroundImage: `url(${bgDarkmode})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center'
      }}
    >
      {/* Tombol Back */}
      <button
        className="absolute top-6 left-6 flex items-center justify-center focus:outline-none group hover:bg-transparent transition-all duration-300"
        onClick={() => navigate('/device-info')}
        style={{ borderRadius: '50%', width: '68px', height: '68px' }}
      >
        <img src={backIcon} alt="Back Icon" className="w-10 h-10" />
      </button>

      <h2 className="text-3xl font-semibold absolute top-[50px]">HISTORY</h2>

      <div className="relative mt-36 w-[1283px]">
        {/* Input Search */}
        <div className="absolute top-[-52px] right-[10px]">
          <input
            type="text"
            placeholder="SEARCH..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="bg-transparent border border-teal-400 px-4 py-2 rounded-md text-white focus:outline-none placeholder-gray-500"
            style={{ width: '275px', height: '40px' }}
          />
        </div>

        <div
          className="relative w-full p-10 shadow-lg text-center"
          style={{
            backgroundImage: `url(${borderImage})`,
            backgroundPosition: 'center',
            backgroundSize: 'contain',
            backgroundRepeat: 'no-repeat',
            height: '700px'
          }}
        >
          <div
            style={{
              backgroundColor: 'rgba(0, 0, 0, 0.6)',
              height: '544px',
              overflowY: itemsPerPage > 10 ? 'auto' : 'visible'
            }}
          >
            <table className="table-auto w-full text-left text-sm">
              <thead style={{ backgroundColor: '#00B3A2' }}>
                <tr className="text-black">
                  {/* Kolom No */}
                  <th className="p-2 text-center">
                    <div className="flex items-center justify-center">
                      No
                      <img
                        src={filterIcon}
                        alt="Filter Icon"
                        className="ml-1 w-3 h-3 cursor-pointer"
                        onClick={() => handleSort('number')}
                      />
                    </div>
                  </th>
                  {/* Kolom Name */}
                  <th className="p-2 text-center">Name</th>
                  {/* Kolom Model */}
                  <th className="p-2 text-center">
                    <div className="flex items-center justify-center">Model</div>
                  </th>
                  {/* Kolom IMEI */}
                  <th className="p-2 text-center">IMEI</th>
                  {/* Kolom Security Patch */}
                  <th className="p-2 text-center">Security Patch</th>
                  {/* Kolom Last Scan */}
                  <th className="p-2 text-center">
                    <div className="flex items-center justify-center">
                      Last Scan
                      <img
                        src={filterIcon}
                        alt="Filter Icon"
                        className="ml-1 w-3 h-3 cursor-pointer"
                        onClick={() => handleSort('lastScan')}
                      />
                    </div>
                  </th>
                  {/* Kolom Security Percentage */}
                  <th className="p-2 text-center">
                    <div className="flex items-center">
                      Security Percentage
                      <img
                        src={filterIcon}
                        alt="Filter Icon"
                        className="ml-1 w-3 h-3 cursor-pointer"
                        onClick={() => handleSort('securityPercentage')}
                      />
                    </div>
                  </th>
                  {/* Kolom Scan Type */}
                  <th className="p-2">
                    <div className="flex items-center">
                      Type Scan
                      <img
                        src={filterIcon}
                        alt="Filter Icon"
                        className="ml-1 w-3 h-3 cursor-pointer"
                        onClick={() => handleSort('scanType')}
                      />
                    </div>
                  </th>
                  {/* Kolom Action */}
                  <th className="p-2 text-center">Action</th>
                </tr>
              </thead>
              <tbody>
                {isLoading
                  ? // Menampilkan skeleton untuk setiap kolom selama loading
                    Array.from({ length: itemsPerPage }).map((_, idx) => (
                      <tr key={idx}>
                        {Array.from({ length: 8 }).map((__, colIdx) => (
                          <td key={colIdx} className="p-2 text-center">
                            <Skeleton />
                          </td>
                        ))}
                      </tr>
                    ))
                  : currentData.map((item) => (
                      <tr
                        key={item.scan_id}
                        className="border-b border-teal-400 hover:bg-[#083732] transition"
                      >
                        <td className="p-2 text-center">{item.no}</td>
                        <td className="p-2 text-center">{item.name}</td>
                        <td className="p-2 text-center">{item.model}</td>
                        <td className="p-2 text-center">{item.imei1}</td>
                        <td className="p-2 text-center">{item.security_patch}</td>
                        <td className="p-2 text-center">{item.last_scan}</td>
                        <td className="p-2 text-center">{item.security_percentage}</td>
                        <td className="p-2 text-center">{item.scan_type}</td>
                        <td className="p-2 text-center">
                          <button
                            className="bg-[#064039] border border-teal-400 px-4 py-1"
                            onClick={() => handleDetail(item)}
                          >
                            DETAIL
                          </button>
                        </td>
                      </tr>
                    ))}
              </tbody>
            </table>
          </div>

          {/* Kontrol Dropdown dan Pagination */}
          <div className="mt-4 flex justify-between items-center px-4 relative">
            {/* Dropdown untuk memilih jumlah item per halaman */}
            <div className="relative inline-block text-left">
              <button
                type="button"
                className="inline-flex w-full justify-center gap-x-1.5 rounded-md bg-[#091817] px-3 py-2 text-sm text-[#fff] shadow-sm hover:bg-[#1a2c2b]"
                onClick={() => setDropdownOpen(!dropdownOpen)}
              >
                Showing {itemsPerPage}
                <svg
                  className="-mr-1 h-5 w-5 text-[#00FFE7]"
                  viewBox="0 0 20 20"
                  fill="currentColor"
                  aria-hidden="true"
                >
                  <path
                    fillRule="evenodd"
                    d="M5.22 8.22a.75.75 0 0 1 1.06 0L10 11.94l3.72-3.72a.75.75 0 1 1 1.06 1.06l-4.25 4.25a.75.75 0 0 1-1.06 0L5.22 9.28a.75.75 0 0 1 0-1.06Z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
              {dropdownOpen && (
                <div className="absolute right-0 z-10 mt-2 w-56 origin-top-right rounded-md bg-[#091817] shadow-lg ring-1 ring-teal-400 ring-opacity-5 focus:outline-none">
                  <div className="py-1">
                    {[5, 10, 25].map((num) => (
                      <button
                        key={num}
                        className="block w-full text-left px-4 py-2 text-sm text-[#00FFE7] hover:bg-teal-700"
                        onClick={() => handleItemsPerPageChange(num)}
                      >
                        {num} items
                      </button>
                    ))}
                  </div>
                </div>
              )}
            </div>

            {/* Kontrol Pagination */}
            <div className="flex items-center">
              <button
                onClick={() => handlePageChange(currentPage - 1)}
                disabled={currentPage === 1}
                className="px-2 py-1 text-[#00FFE7] rounded-md hover:bg-[#00FFE7] hover:text-black transition"
                style={{ height: '36px' }}
              >
                Prev
              </button>
              <div className="flex space-x-2 mx-4">
                {Array.from({ length: totalPages }).map((_, index) => (
                  <button
                    key={index + 1}
                    onClick={() => handlePageChange(index + 1)}
                    className={`px-2 py-1 border border-[#00FFE7] rounded-md transition ${
                      currentPage === index + 1
                        ? 'bg-[#00FFE7] text-black'
                        : 'text-[#00FFE7] hover:bg-[#00FFE7] hover:text-black'
                    }`}
                    style={{ height: '36px', width: '36px' }}
                  >
                    {index + 1}
                  </button>
                ))}
              </div>
              <button
                onClick={() => handlePageChange(currentPage + 1)}
                disabled={currentPage === totalPages}
                className="px-2 py-1 text-[#00FFE7] rounded-md hover:bg-[#00FFE7] hover:text-black transition"
                style={{ height: '36px' }}
              >
                Next
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default HistoryPage
