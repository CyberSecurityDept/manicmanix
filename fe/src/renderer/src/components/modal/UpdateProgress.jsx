import { useState, useEffect } from 'react'
import plusSign from '../../assets/plus-sign.svg'
import ArrowPattern from '../ArrowPattern'

const UpdateProgress = ({ onClose }) => {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    // Handler untuk update progress FE
    const handleProgress = (progressObj) => {
      console.log('Renderer received progress:', progressObj)
      if (progressObj && progressObj.percent) {
        setProgress(Math.floor(progressObj.percent))
      }
    }

    const handleDownloaded = () => {
      setProgress(100)
      setTimeout(() => {
        window.electron.ipcRenderer.send('quit-and-install')
      }, 1000)
    }

    window.electron.ipcRenderer.on('fe-update-progress', handleProgress)
    window.electron.ipcRenderer.on('fe-update-downloaded', handleDownloaded)

    return () => {
      window.electron.ipcRenderer.removeListener('fe-update-progress', handleProgress)
      window.electron.ipcRenderer.removeListener('fe-update-downloaded', handleDownloaded)
    }
  }, [])

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 font-aldrich backdrop-blur-md"
      style={{ background: 'rgba(0, 0, 0, 0.8)' }}
    >
      <div className="relative w-[801px] h-[305px] border-2 border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] flex flex-col items-center justify-center p-8">
        <img src={plusSign} alt="Plus Sign" className="absolute top-[-13px] left-[-13px] w-6 h-6" />
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