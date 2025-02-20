import React from 'react'
import headerBg from '../assets/Header-full.png'

const Header = () => {
  return (
    <div
      className="bg-contain bg-center bg-no-repeat w-screen h-[23vh] flex flex-col items-center justify-start pt-6 z-10"
      style={{ backgroundImage: `url(${headerBg})` }}
    >
      <h1 className="text-3xl font-bold text-white tracking-widest uppercase">Study Kasus</h1>
    </div>
  )
}

export default Header
