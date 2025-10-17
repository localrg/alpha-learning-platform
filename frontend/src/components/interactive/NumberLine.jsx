import { useState, useEffect, useRef } from 'react';
import './NumberLine.css';

const NumberLine = ({ config, onInteraction }) => {
  const {
    min = 0,
    max = 20,
    start_value = 0,
    operation = 'add',
    operand = 0,
    show_jumps = true,
    show_labels = true,
    instructions = ''
  } = config;

  const [currentValue, setCurrentValue] = useState(start_value);
  const [isDragging, setIsDragging] = useState(false);
  const [showAnimation, setShowAnimation] = useState(false);
  const lineRef = useRef(null);

  const range = max - min;
  const result = operation === 'add' ? start_value + operand : start_value - operand;

  // Calculate position on number line (0-100%)
  const getPosition = (value) => {
    return ((value - min) / range) * 100;
  };

  // Handle drag
  const handleMouseDown = (e) => {
    setIsDragging(true);
  };

  const handleMouseMove = (e) => {
    if (!isDragging || !lineRef.current) return;

    const rect = lineRef.current.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const percentage = Math.max(0, Math.min(100, (x / rect.width) * 100));
    const value = Math.round(min + (percentage / 100) * range);

    setCurrentValue(value);
    
    if (onInteraction) {
      onInteraction({
        action: 'drag_marker',
        from: currentValue,
        to: value
      });
    }
  };

  const handleMouseUp = () => {
    setIsDragging(false);
  };

  useEffect(() => {
    if (isDragging) {
      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      return () => {
        window.removeEventListener('mousemove', handleMouseMove);
        window.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, currentValue]);

  // Animate jumps
  const animateJumps = () => {
    setShowAnimation(true);
    setTimeout(() => setShowAnimation(false), 2000);
    
    if (onInteraction) {
      onInteraction({
        action: 'show_animation',
        operation,
        start: start_value,
        operand
      });
    }
  };

  // Generate tick marks
  const ticks = [];
  const tickInterval = range <= 20 ? 1 : range <= 50 ? 5 : 10;
  
  for (let i = min; i <= max; i += tickInterval) {
    ticks.push(i);
  }

  return (
    <div className="number-line-container">
      {instructions && (
        <div className="instructions">
          <span className="instruction-icon">💡</span>
          {instructions}
        </div>
      )}

      <div className="number-line-wrapper">
        {/* Number Line */}
        <div className="number-line" ref={lineRef}>
          {/* Line */}
          <div className="line-track" />

          {/* Tick marks and labels */}
          {ticks.map((value) => (
            <div
              key={value}
              className="tick"
              style={{ left: `${getPosition(value)}%` }}
            >
              <div className="tick-mark" />
              {show_labels && <div className="tick-label">{value}</div>}
            </div>
          ))}

          {/* Start marker */}
          <div
            className="marker start-marker"
            style={{ left: `${getPosition(start_value)}%` }}
          >
            <div className="marker-dot" />
            <div className="marker-label">Start: {start_value}</div>
          </div>

          {/* Current/draggable marker */}
          <div
            className={`marker current-marker ${isDragging ? 'dragging' : ''}`}
            style={{ left: `${getPosition(currentValue)}%` }}
            onMouseDown={handleMouseDown}
          >
            <div className="marker-dot" />
            <div className="marker-label">{currentValue}</div>
          </div>

          {/* Jump visualization */}
          {show_jumps && showAnimation && (
            <div className="jumps-container">
              {Array.from({ length: Math.abs(operand) }).map((_, i) => {
                const jumpStart = operation === 'add' 
                  ? start_value + i 
                  : start_value - i;
                const jumpEnd = operation === 'add'
                  ? jumpStart + 1
                  : jumpStart - 1;
                
                return (
                  <div
                    key={i}
                    className={`jump ${operation}`}
                    style={{
                      left: `${getPosition(Math.min(jumpStart, jumpEnd))}%`,
                      width: `${Math.abs(getPosition(jumpEnd) - getPosition(jumpStart))}%`,
                      animationDelay: `${i * 0.3}s`
                    }}
                  >
                    <div className="jump-arrow" />
                  </div>
                );
              })}
            </div>
          )}

          {/* Result marker */}
          {result >= min && result <= max && (
            <div
              className="marker result-marker"
              style={{ left: `${getPosition(result)}%` }}
            >
              <div className="marker-dot" />
              <div className="marker-label">Result: {result}</div>
            </div>
          )}
        </div>
      </div>

      {/* Controls */}
      <div className="controls">
        <button className="btn-animate" onClick={animateJumps}>
          ▶ Show {operation === 'add' ? 'Addition' : 'Subtraction'}
        </button>
        <button className="btn-reset" onClick={() => setCurrentValue(start_value)}>
          ↺ Reset
        </button>
      </div>

      {/* Equation display */}
      <div className="equation-display">
        <span className="equation">
          {start_value} {operation === 'add' ? '+' : '−'} {Math.abs(operand)} = {result}
        </span>
      </div>
    </div>
  );
};

export default NumberLine;

