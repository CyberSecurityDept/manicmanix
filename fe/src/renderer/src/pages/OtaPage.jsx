import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import bgDarkmode from '../assets/bg-darkmode.png'
import plusSign from '../assets/plus-sign.svg'
import Border from '../assets/border/App-border.svg'
import UpdateBorder from '../assets/border/update.svg'
import UpdateModal from '../components/modal/Update'
import NewVersionModal from '../components/modal/NewVersion'
import UpdateProgress from '../components/modal/UpdateProgress'
import backIcon from '../assets/back-Icon.svg'

const OTA = () => {
  const navigate = useNavigate()
  const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false)
  const [isNewVersionModalOpen, setIsNewVersionModalOpen] = useState(false)
  const [isUpdateProgressModalOpen, setIsUpdateProgressModalOpen] = useState(false)
  const [updateData, setUpdateData] = useState(null)

  const checkAPPUpdate = () => {
    // Tampilkan modal pengecekan update
    setIsUpdateModalOpen(true)
    // Mulai cek update FE melalui IPC
    window.electron.ipcRenderer.send('start-fe-update')
  }

  // Dengar status update FE dari main process
  useEffect(() => {
    const handleFeUpdateStatus = (feStatus) => {
      if (feStatus.updateAvailable) {
        // Simpan data update (misalnya versi terbaru) jika diperlukan
        setUpdateData(feStatus)
        setIsUpdateModalOpen(false)
        setIsNewVersionModalOpen(true)
      } else {
        setIsUpdateModalOpen(false)
        alert('You are using the latest version.')
      }
    }
    window.electron.ipcRenderer.on('fe-update-status', handleFeUpdateStatus)

    return () => {
      window.electron.ipcRenderer.removeListener('fe-update-status', handleFeUpdateStatus)
    }
  }, [])

  const handleUpdate = () => {
    // Tutup modal New Version dan tampilkan modal progress update FE
    setIsNewVersionModalOpen(false)
    setIsUpdateProgressModalOpen(true)
    // Mulai proses download update FE (jika belum berjalan, main process akan mengirim progress)
    // Tidak perlu panggil endpoint BE karena fokus hanya update FE
  }

  return (
    <div
      className="w-full h-screen relative bg-cover flex flex-col items-center justify-center"
      style={{ backgroundImage: `url(${bgDarkmode})` }}
    >
      {/* Tombol Back */}
      <button className="absolute top-6 left-6" onClick={() => navigate('/')}>
        <img src={backIcon} alt="Back Icon" className="w-[48px] h-[48px]" />
      </button>

      <h1 className="text-white text-3xl font-semibold mb-10">OTA</h1>

      {/* APP & CYBER Section */}
      <div className="w-[1022px] h-[222px] relative border-2 border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] flex justify-around items-center mb-8">
        <img src={plusSign} alt="Plus Sign" className="absolute top-[-14px] left-[-13px] w-6 h-6" />
        <img src={plusSign} alt="Plus Sign" className="absolute bottom-[-12px] right-[-12px] w-6 h-6" />

        {/* APP Box */}
        <div
          className="w-[403px] h-[123px] bg-cover bg-no-repeat border border-[#05564F] flex flex-col justify-center items-center bg-gradient-to-b from-[#0C1E1B] to-[#0C1612]"
          style={{ backgroundImage: `url(${Border})` }}
        >
          <h2 className="text-white text-lg mb-2">APP V1.1.0.0</h2>
          <button
            onClick={checkAPPUpdate}
            className="text-white py-1 px-4"
            style={{
              backgroundImage: `url(${UpdateBorder})`,
              backgroundSize: 'cover',
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'center',
              width: '228px',
              height: '37px',
              color: '#FFFFFF'
            }}
          >
            CHECK UPDATE
          </button>
        </div>

        {/* CYBER Box (Bisa disesuaikan, misal tampilkan pesan "Not implemented") */}
        <div
          className="w-[403px] h-[123px] bg-cover bg-no-repeat border border-[#05564F] flex flex-col justify-center items-center bg-gradient-to-b from-[#0C1E1B] to-[#0C1612]"
          style={{ backgroundImage: `url(${Border})` }}
        >
          <h2 className="text-white text-lg mb-2">CYBER V1.2.3.4</h2>
          <button
            onClick={() => alert('Not implemented')}
            className="text-white py-1 px-4"
            style={{
              backgroundImage: `url(${UpdateBorder})`,
              backgroundSize: 'cover',
              backgroundRepeat: 'no-repeat',
              backgroundPosition: 'center',
              width: '228px',
              height: '37px',
              color: '#FFFFFF'
            }}
          >
            CHECK UPDATE
          </button>
        </div>
      </div>

      {/* UPDATE LOG Section */}
      <div className="w-[1022px] h-[444px] relative border-2 border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] p-6">
        <img src={plusSign} alt="Plus Sign" className="absolute top-[-14px] left-[-13px] w-6 h-6" />
        <img src={plusSign} alt="Plus Sign" className="absolute bottom-[-12px] right-[-12px] w-6 h-6" />

        <div className="flex justify-between items-center px-10 py-4 border-b border-[#05564F]">
          <h3 className="text-white text-xl font-semibold">Version Release</h3>
          <button className="bg-transparent border border-[#0C9A8D] text-[#FFFFFF] py-1 px-4 rounded hover:border-[#00FFE7]">
            VIEW MORE
          </button>
        </div>

        <div className="flex justify-between items-center px-10 py-2 bg-[#0C9A8D] text-[#091817] font-semibold">
          <div className="text-center w-1/2">Patch</div>
          <div className="text-center w-1/2">Data</div>
        </div>

        <div className="overflow-y-auto h-[320px]">
          {['APK V1.1.12', 'APK V1.1.12', 'CYBER V1.1.12'].map((patch, index) => (
            <div key={index} className="flex justify-between items-center px-10 py-2 text-white border-t border-[#05564F]">
              <div className="w-1/2 text-center">{patch}</div>
              <div className="w-1/2 text-center">2024-08-05</div>
            </div>
          ))}
        </div>
      </div>

      {/* Modal Update */}
      {isUpdateModalOpen && (
        <UpdateModal onClose={() => setIsUpdateModalOpen(false)} updateData={updateData} />
      )}

      {/* Modal New Version */}
      {isNewVersionModalOpen && (
        <NewVersionModal
          onClose={() => setIsNewVersionModalOpen(false)}
          onUpdate={handleUpdate}
          updateData={updateData}
        />
      )}

      {/* Modal Update Progress */}
      {isUpdateProgressModalOpen && (
        <UpdateProgress onClose={() => setIsUpdateProgressModalOpen(false)} />
      )}

      {/* OTA Button */}
      <button
        className="absolute bottom-[42px] right-[52px] flex items-center justify-center w-[60px] h-[60px] bg-gradient-to-b from-[#0C1612] to-[#091817] border-t border-b border-[#4FD1C5] text-sm font-bold text-white hover:bg-teal-700"
        onClick={() => navigate('/info')}
      >
        <span className="text-2xl">i</span>
      </button>
    </div>
  )
}

export default OTA