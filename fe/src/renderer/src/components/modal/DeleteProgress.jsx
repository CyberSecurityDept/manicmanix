import { useEffect } from 'react'
import plusSign from '../../assets/plus-sign.svg'
import ArrowPattern from '../ArrowPattern'

const DeleteProgressModal = ({ progress, onClose, onProgressComplete }) => {
  useEffect(() => {
    if (progress >= 100) {
      setTimeout(() => {
        onProgressComplete()
        onClose()
      }, 500)
    }
  }, [progress, onClose, onProgressComplete])

  return (
    <div
      className="fixed inset-0 flex items-center justify-center z-50 font-aldrich backdrop-blur-md"
      style={{ background: 'rgba(0, 0, 0, 0.8)' }}
    >
      <div className="relative w-[801px] h-[422px] flex flex-col items-center border-2 border-y-[#0C9A8D] border-x-[#05564F] bg-gradient-to-b from-[#091817] to-[#0C1612] justify-center p-8">
        <img src={plusSign} alt="Plus Sign" className="absolute top-[-13px] left-[-13px] w-6 h-6" />
        <img
          src={plusSign}
          alt="Plus Sign"
          className="absolute bottom-[-13px] right-[-13px] w-6 h-6"
        />
        <h1 className="text-2xl mb-4 font-bold text-[#00E6E6]">Removing process {progress}%</h1>
        <div className="w-[663px] h-[45px] border border-[#00E6E6] flex items-center justify-center mb-4 p-2">
          <ArrowPattern progress={progress} />
        </div>
      </div>
    </div>
  )
}

export default DeleteProgressModal
