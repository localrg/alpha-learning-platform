import { useState, useEffect } from 'react';
import './ArrayGrid.css';

const ArrayGrid = ({ config, onInteraction }) => {
  const {
    rows = 3,
    cols = 4,
    editable = true,
    show_equation = true,
    allow_resize = false,
    instructions = ''
  } = config;

  const [gridRows, setGridRows] = useState(rows);
  const [gridCols, setGridCols] = useState(cols);
  const [filledCells, setFilledCells] = useState(new Set());

  // Initialize filled cells
  useEffect(() => {
    if (!editable) {
      // Fill all cells if not editable
      const allCells = new Set();
      for (let r = 0; r < gridRows; r++) {
        for (let c = 0; c < gridCols; c++) {
          allCells.add(`${r}-${c}`);
        }
      }
      setFilledCells(allCells);
    }
  }, [gridRows, gridCols, editable]);

  const toggleCell = (row, col) => {
    if (!editable) return;

    const cellKey = `${row}-${col}`;
    const newFilled = new Set(filledCells);

    if (newFilled.has(cellKey)) {
      newFilled.delete(cellKey);
    } else {
      newFilled.add(cellKey);
    }

    setFilledCells(newFilled);

    if (onInteraction) {
      onInteraction({
        action: 'toggle_cell',
        row,
        col,
        filled: !filledCells.has(cellKey),
        total_filled: newFilled.size
      });
    }
  };

  const fillAll = () => {
    const allCells = new Set();
    for (let r = 0; r < gridRows; r++) {
      for (let c = 0; c < gridCols; c++) {
        allCells.add(`${r}-${c}`);
      }
    }
    setFilledCells(allCells);

    if (onInteraction) {
      onInteraction({
        action: 'fill_all',
        rows: gridRows,
        cols: gridCols
      });
    }
  };

  const clearAll = () => {
    setFilledCells(new Set());

    if (onInteraction) {
      onInteraction({
        action: 'clear_all'
      });
    }
  };

  const changeSize = (newRows, newCols) => {
    setGridRows(newRows);
    setGridCols(newCols);
    setFilledCells(new Set());

    if (onInteraction) {
      onInteraction({
        action: 'resize_grid',
        rows: newRows,
        cols: newCols
      });
    }
  };

  const totalCells = gridRows * gridCols;
  const filledCount = filledCells.size;

  return (
    <div className="array-grid-container">
      {instructions && (
        <div className="instructions">
          <span className="instruction-icon">💡</span>
          {instructions}
        </div>
      )}

      {/* Grid */}
      <div className="grid-wrapper">
        <div 
          className="array-grid"
          style={{
            gridTemplateRows: `repeat(${gridRows}, 1fr)`,
            gridTemplateColumns: `repeat(${gridCols}, 1fr)`
          }}
        >
          {Array.from({ length: gridRows }).map((_, rowIndex) =>
            Array.from({ length: gridCols }).map((_, colIndex) => {
              const cellKey = `${rowIndex}-${colIndex}`;
              const isFilled = filledCells.has(cellKey);

              return (
                <div
                  key={cellKey}
                  className={`grid-cell ${isFilled ? 'filled' : ''} ${editable ? 'editable' : ''}`}
                  onClick={() => toggleCell(rowIndex, colIndex)}
                >
                  {isFilled && <div className="cell-dot" />}
                </div>
              );
            })
          )}
        </div>

        {/* Row and Column Labels */}
        <div className="grid-labels">
          <div className="row-label">{gridRows} rows</div>
          <div className="col-label">{gridCols} columns</div>
        </div>
      </div>

      {/* Controls */}
      <div className="controls">
        {editable && (
          <>
            <button className="btn-fill" onClick={fillAll}>
              Fill All
            </button>
            <button className="btn-clear" onClick={clearAll}>
              Clear All
            </button>
          </>
        )}

        {allow_resize && (
          <div className="resize-controls">
            <div className="resize-group">
              <label>Rows:</label>
              <button onClick={() => changeSize(Math.max(1, gridRows - 1), gridCols)}>−</button>
              <span>{gridRows}</span>
              <button onClick={() => changeSize(Math.min(10, gridRows + 1), gridCols)}>+</button>
            </div>
            <div className="resize-group">
              <label>Cols:</label>
              <button onClick={() => changeSize(gridRows, Math.max(1, gridCols - 1))}>−</button>
              <span>{gridCols}</span>
              <button onClick={() => changeSize(gridRows, Math.min(10, gridCols + 1))}>+</button>
            </div>
          </div>
        )}
      </div>

      {/* Equation Display */}
      {show_equation && (
        <div className="equation-display">
          <div className="equation-parts">
            <span className="equation-part">
              <span className="value">{gridRows}</span>
              <span className="label">rows</span>
            </span>
            <span className="operator">×</span>
            <span className="equation-part">
              <span className="value">{gridCols}</span>
              <span className="label">columns</span>
            </span>
            <span className="operator">=</span>
            <span className="equation-part result">
              <span className="value">{totalCells}</span>
              <span className="label">total</span>
            </span>
          </div>
          
          {editable && filledCount !== totalCells && (
            <div className="fill-status">
              {filledCount} of {totalCells} cells filled
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default ArrayGrid;

