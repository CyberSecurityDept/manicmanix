import { useState, useEffect } from 'react'
import plusSign from '../../assets/plus-sign.svg'
import ArrowPattern from '../ArrowPattern'

const UpdateProgress = ({ onClose, updateType, cyberData }) => {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (updateType === 'cyber') {
      // Untuk update cyber:
      // Jika data menunjukkan update berhasil, langsung set progress ke 100% dan tutup modal.
      if (
        cyberData &&
        cyberData.message === "Cyber version and IOCs updated successfully."
      ) {
        setProgress(100)
        const timeout = setTimeout(() => {
          onClose()
        }, 1000)
        return () => clearTimeout(timeout)
      }
      // Jika belum, simulasikan progress dengan interval 1 detik.
      const interval = setInterval(() => {
        setProgress((prevProgress) => {
          const newProgress = prevProgress + 5
          if (newProgress >= 100) {
            clearInterval(interval)
            setTimeout(() => {
              onClose()
            }, 0)
            return 100
          }
          return newProgress
        })
      }, 1000)
      return () => clearInterval(interval)
    } else {
      // Untuk update app:
      // Simulasikan progress dengan interval 500ms.
      let simulationInterval = setInterval(() => {
        setProgress((prevProgress) => {
          const newProgress = prevProgress + 5
          if (newProgress >= 100) {
            clearInterval(simulationInterval)
            setProgress(100)
            setTimeout(() => {
              window.electron.ipcRenderer.send('quit-and-install')
            }, 1000)
            return 100
          }
          return newProgress
        })
      }, 500)
  
      // Jika event 'fe-update-downloaded' diterima, hentikan simulasi dan trigger quit-and-install.
      const handleDownloaded = () => {
        clearInterval(simulationInterval)
        setProgress(100)
        setTimeout(() => {
          window.electron.ipcRenderer.send('quit-and-install')
        }, 1000)
      }
  
      window.electron.ipcRenderer.on('fe-update-downloaded', handleDownloaded)
  
      return () => {
        clearInterval(simulationInterval)
        window.electron.ipcRenderer.removeListener('fe-update-downloaded', handleDownloaded)
      }
    }
  }, [onClose, updateType, cyberData])

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 font-aldrich backdrop-blur-md"
      style={{ background: 'rgba(0, 0, 0, 0.8)' }}
    >
      <div className="relative w-[801px] h-[305px] border-2 border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] flex flex-col items-center justify-center p-8">
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute top-[-13px] left-[-13px] w-6 h-6"
        />
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute bottom-[-13px] right-[-12px] w-6 h-6"
        />
        <div className="w-[663px] h-[45px] border border-[#00E6E6] flex items-center justify-center p-2">
          <ArrowPattern progress={progress} />
        </div>
        <p className="text-[#00FFE7] text-3xl mt-10">Updating {progress}%</p>
      </div>
    </div>
  )
}

export default UpdateProgress
