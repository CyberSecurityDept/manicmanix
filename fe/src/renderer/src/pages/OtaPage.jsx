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
  const BASE_URL = import.meta.env.VITE_BASE_URL
  const UPDATE_APP_URL = '/v1/update-app'
  const UPDATE_Cyber_URL = '/v1/update-cyber-version'
  const CHECK_APP_URL = '/v1/check-update-app'
  const CHECK_Cyber_URL = '/v1/check-update-cyber'
  const LIST_VERSION_URL = '/v1/list-version'

  const navigate = useNavigate()
  const [isUpdateModalOpen, setIsUpdateModalOpen] = useState(false)
  const [isNewVersionModalOpen, setIsNewVersionModalOpen] = useState(false)
  const [isUpdateProgressModalOpen, setIsUpdateProgressModalOpen] = useState(false)
  const [updateData, setUpdateData] = useState(null)
  const [versionData, setVersionData] = useState(null)
  // Menyimpan tipe update: 'app' atau 'cyber'
  const [updateType, setUpdateType] = useState(null)

  // Fetch list version ketika komponen mount
  useEffect(() => {
    const fetchVersionList = async () => {
      try {
        const response = await fetch(`${BASE_URL}${LIST_VERSION_URL}`, {
          method: 'GET',
          headers: {
            accept: 'application/json',
            'Content-Type': 'application/json'
          }
        })
        if (!response.ok) {
          throw new Error(`Status: ${response.status}`)
        }
        const result = await response.json()
        // result.data berisi app_versions dan cyber_versions
        setVersionData(result.data)
      } catch (error) {
        console.error('Error fetching version list:', error)
      }
    }

    fetchVersionList()
  }, [BASE_URL])

  // Fungsi pengecekan update untuk APP dan CYBER
  const checkUpdate = async (type) => {
    setUpdateType(type)
    // Tampilkan modal loading update
    setIsUpdateModalOpen(true)

    // Tentukan URL sesuai tipe update
    const url =
      type === 'app'
        ? `${BASE_URL}${CHECK_APP_URL}`
        : `${BASE_URL}${CHECK_Cyber_URL}`

    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          accept: 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      })

      if (!response.ok) {
        throw new Error(`Status: ${response.status}`)
      }

      const data = await response.json()
      setUpdateData(data)

      if (type === 'app') {
        // Pengecekan FE melalui IPC untuk APP
        window.electron.ipcRenderer.send('start-fe-update')
        window.electron.ipcRenderer.on('fe-update-status', (feStatus) => {
          if (data.updated_version !== data.latest_version_tag || feStatus.updateAvailable) {
            setIsNewVersionModalOpen(true)
          } else {
          }
        })
      } else {
        // Untuk CYBER, cek properti update_available
        if (data.update_available) {
          setIsNewVersionModalOpen(true)
        } else {
        }
      }
    } catch (error) {
      console.error(`Error checking ${type} update:`, error)
      setIsUpdateModalOpen(false)
      alert(`Error: ${error.message}`)
    }
  }

  // Fungsi untuk memproses update (untuk APP dan CYBER)
  const handleUpdate = async () => {
    setIsNewVersionModalOpen(false)
    setIsUpdateProgressModalOpen(true)
  
    const url =
      updateType === 'app'
        ? `${BASE_URL}${UPDATE_APP_URL}`
        : `${BASE_URL}${UPDATE_Cyber_URL}`
  
    try {
      const response = await fetch(url, {
        method: 'POST',
        headers: {
          accept: 'application/json',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({})
      })
  
      if (!response.ok) {
        throw new Error(`Network response was not ok. Status: ${response.status}`)
      }
  
      const data = await response.json()
  
      if (updateType === 'app') {
        // Lakukan pengecekan terhadap response yang diharapkan
        console.log("ini typpe update yang dilakukan: ".updateType)
        if (
          data.message === 'updated app successfully.' &&
          data.download_output === 'Checked out to latest tag.'
        ) {
          // Hanya trigger update jika respon sesuai
          window.electron.ipcRenderer.send('start-fe-update')
          setIsUpdateProgressModalOpen(false)
          alert('Update aplikasi berhasil.')
          window.electron.ipcRenderer.once('fe-update-downloaded', () => {
            // Tanyakan ke user apakah ingin langsung install update
            const userConfirmed = window.confirm('Update telah selesai di-download. Install sekarang?')
            if (userConfirmed) {
              window.electron.ipcRenderer.send('quit-and-install')
            }
          })
        } else {
          throw new Error(data.message || 'Update gagal')
        }
      } else {
        if (data.message === "Cyber version and IOCs updated successfully.") {
          setIsUpdateProgressModalOpen(false)
        } else {
          throw new Error(data.message || 'Cyber update failed')
        }
      }
    } catch (error) {
      console.error(`Error updating ${updateType} version:`, error)
      setIsUpdateProgressModalOpen(false)
      alert(`Failed to update ${updateType} version. Error: ${error.message}`)
    }
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
          <h2 className="text-white text-lg mb-2">
            APP {''}
            {versionData && versionData.app_versions.length > 0
              ? versionData.app_versions[0].app_version
              : '1.1.1.2'}
          </h2>
          <button
            onClick={() => checkUpdate('app')}
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

        {/* CYBER Box */}
        <div
          className="w-[403px] h-[123px] bg-cover bg-no-repeat border border-[#05564F] flex flex-col justify-center items-center bg-gradient-to-b from-[#0C1E1B] to-[#0C1612]"
          style={{ backgroundImage: `url(${Border})` }}
        >
          <h2 className="text-white text-lg mb-2">
            CYBER V.
            {versionData && versionData.cyber_versions.length > 0
              ? versionData.cyber_versions[0].cyber_version
              : 'V1.2.3.4'}
          </h2>
          <button
            onClick={() => checkUpdate('cyber')}
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
        </div>

        <div className="flex justify-between items-center px-10 py-2 bg-[#0C9A8D] text-[#091817] font-semibold">
          <div className="text-center w-1/2">Patch</div>
          <div className="text-center w-1/2">Date</div>
        </div>

        <div className="overflow-y-auto h-[320px]">
          {versionData ? (
            <>
              {versionData.app_versions.map((item, index) => (
                <div
                  key={`app-${index}`}
                  className="flex justify-between items-center px-10 py-2 text-white border-t border-[#05564F]"
                >
                  <div className="w-1/2 text-center">{item.app_version}</div>
                  <div className="w-1/2 text-center">{item.datetime}</div>
                </div>
              ))}
              {versionData.cyber_versions.map((item, index) => (
                <div
                  key={`cyber-${index}`}
                  className="flex justify-between items-center px-10 py-2 text-white border-t border-[#05564F]"
                >
                  <div className="w-1/2 text-center">{item.cyber_version}</div>
                  <div className="w-1/2 text-center">{item.datetime}</div>
                </div>
              ))}
            </>
          ) : (
            <p className="text-white text-center mt-10">Loading version data...</p>
          )}
        </div>
      </div>

      {/* Modal Update (Loading) */}
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
        className="absolute bottom-[42px] right-[52px] flex items-center justify-center w-[60px] h-[60px] bg-gradient-to-b from-[#0C1612] to-[#091817] border border-[#4FD1C5] text-sm font-bold text-white hover:bg-teal-700"
        onClick={() => navigate('/info')}
      >
        <span className="text-2xl">i</span>
      </button>
    </div>
  )
}

export default OTA
