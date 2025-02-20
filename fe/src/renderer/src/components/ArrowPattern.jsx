import React from 'react'

const ArrowPattern = ({ progress }) => {
  const arrows = new Array(50).fill(null) // Number of arrows
  const maxProgress = 100 // Maximum progress percentage
  const filledArrows = Math.round((progress / maxProgress) * arrows.length) // Number of arrows to be filled

  return (
    <div className="flex w-full h-full justify-center items-center">
      {arrows.map((_, index) => (
        <svg
          key={index}
          xmlns="http://www.w3.org/2000/svg"
          viewBox="0 0 21 21"
          fill={index < filledArrows ? '#00FFE7' : '#0A332F'} // Fill color based on progress
          className="w-5 h-5 sm:w-6 sm:h-6 md:w-8 md:h-8" // Adjust size based on screen size
        >
          {/* Path for right-pointing arrow */}
          <path d="M8.87793 11L0.87793 21H11.8779L20.3779 11L10.8779 0H0.87793L8.87793 11Z" />
        </svg>
      ))}
    </div>
  )
}

export default ArrowPattern
