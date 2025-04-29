
import React from 'react';
import { MathJax } from 'better-react-mathjax';


const MathRenderer = ({ text }) => {
  if (!text) return null;
  
  return (
    // Wrap in a span or div as appropriate for flow
    <span>
      <MathJax hideUntilTypeset="first">
          {text}
      </MathJax>
    </span>
  );
};

export default MathRenderer;