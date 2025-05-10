import React from 'react';

// Standard import approach
import examplePoster from '../../assets/example_poster.png';
import examplePosterLight from '../../assets/example_poster_light.png';
import dummyPosterDark from '../../assets/posters/dummy_poster_dark.png';
import dummyPosterLight from '../../assets/posters/dummy_poster_light.png';

const DirectImageTest: React.FC = () => {
  return (
    <div className="space-y-6">
      <h2 className="text-xl font-bold">Image Loading Test</h2>
      
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Standard Import Method</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm mb-2">Example Poster</p>
            <img 
              src={examplePoster} 
              alt="Example Poster" 
              width={200} 
              className="border border-gray-300" 
            />
          </div>
          <div>
            <p className="text-sm mb-2">Example Poster Light</p>
            <img 
              src={examplePosterLight} 
              alt="Example Poster Light" 
              width={200} 
              className="border border-gray-300" 
            />
          </div>
          <div>
            <p className="text-sm mb-2">Dummy Poster Dark</p>
            <img 
              src={dummyPosterDark} 
              alt="Dummy Poster Dark" 
              width={200} 
              className="border border-gray-300" 
            />
          </div>
          <div>
            <p className="text-sm mb-2">Dummy Poster Light</p>
            <img 
              src={dummyPosterLight} 
              alt="Dummy Poster Light" 
              width={200} 
              className="border border-gray-300" 
            />
          </div>
        </div>
      </div>
      
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Public URL Method</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm mb-2">Direct Public Path</p>
            <img 
              src="/src/assets/example_poster.png" 
              alt="Example Poster (Public Path)" 
              width={200} 
              className="border border-gray-300" 
            />
          </div>
          <div>
            <p className="text-sm mb-2">Direct Public Path</p>
            <img 
              src="/src/assets/example_poster_light.png" 
              alt="Example Poster Light (Public Path)" 
              width={200} 
              className="border border-gray-300" 
            />
          </div>
        </div>
      </div>
      
      <div className="p-4 bg-gray-100 rounded-md mt-6">
        <p className="text-sm font-semibold">Debug Info:</p>
        <pre className="text-xs overflow-auto whitespace-pre-wrap bg-white p-2 rounded mt-1">
          examplePoster value: {JSON.stringify(examplePoster)}
          <br />
          examplePosterLight value: {JSON.stringify(examplePosterLight)}
          <br />
          dummyPosterDark value: {JSON.stringify(dummyPosterDark)}
          <br />
          dummyPosterLight value: {JSON.stringify(dummyPosterLight)}
        </pre>
      </div>
    </div>
  );
};

export default DirectImageTest;