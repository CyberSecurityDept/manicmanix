import React, { useState, useEffect } from 'react'
import plusSign from '../../assets/plus-sign.svg'
import ArrowPattern from '../ArrowPattern'

const UpdateModal = ({ onClose, updateData }) => {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    if (updateData) {
      // Cek apakah respon berasal dari app box (misalnya memiliki current_tag)
      if (updateData.current_tag !== undefined && updateData.latest_remote_tag !== undefined) {
        const appUpToDate = updateData.current_tag === updateData.latest_remote_tag
        setProgress(100)
        const timeout = setTimeout(() => {
          onClose()
        }, appUpToDate ? 1000 : 300)
        return () => clearTimeout(timeout)
      }
      // Jika respon berasal dari cyber box (menggunakan update_available)
      if (updateData.update_available !== undefined) {
        if (updateData.update_available === false) {
          setProgress(100)
          const timeout = setTimeout(() => {
            onClose()
          }, 1000)
          return () => clearTimeout(timeout)
        } else if (updateData.update_available === true) {
          setProgress(100)
          const timeout = setTimeout(() => {
            onClose()
          }, 300)
          return () => clearTimeout(timeout)
        }
      }
    }

    // Jika updateData belum ada, naikkan progress secara periodik
    const interval = setInterval(() => {
      setProgress((prevProgress) => {
        const newProgress = prevProgress + 10
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
  }, [updateData, onClose])

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

        {updateData ? (
          <p className="text-[#00FFE7] text-3xl mt-10">Checking for updates...</p>
        ) : (
          <p className="text-[#00FFE7] text-3xl mt-10">Checking</p>
        )}
      </div>
    </div>
  )
}

export default UpdateModal
