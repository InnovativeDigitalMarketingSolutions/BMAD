import React from 'react';

interface Agent {
  id: string;
  name: string;
  status: 'online' | 'offline' | 'busy';
  activeSessions: number;
  waitTime: number; // in seconds
  productivity: number; // percentage
  lastActivity: string;
  tasks: string[];
}

interface AgentCardProps {
  agent: Agent;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent }) => {
  const statusColor = {
    online: 'bg-green-500',
    offline: 'bg-gray-300',
    busy: 'bg-yellow-500',
  };

  const statusText = {
    online: 'Online',
    offline: 'Offline',
    busy: 'Busy',
  };

  const formatWaitTime = (seconds: number) => {
    if (seconds === 0) return '0s';
    if (seconds < 60) return `${seconds}s`;
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}m ${remainingSeconds}s`;
  };

  return (
    <div className="max-w-sm rounded overflow-hidden shadow-lg p-4 bg-white hover:shadow-xl transition-shadow duration-200">
      <div className="flex items-center justify-between mb-3">
        <div className={`w-3 h-3 rounded-full ${statusColor[agent.status]} animate-pulse`} />
        <span className={`text-xs px-2 py-1 rounded-full ${
          agent.status === 'online' ? 'bg-green-100 text-green-800' :
          agent.status === 'busy' ? 'bg-yellow-100 text-yellow-800' :
          'bg-gray-100 text-gray-800'
        }`}>
          {statusText[agent.status]}
        </span>
      </div>
      
      <h2 className="text-lg font-bold mb-3 text-gray-900">{agent.name}</h2>
      
      <div className="space-y-2 text-sm">
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Active Sessions:</span>
          <span className="font-semibold text-gray-900">{agent.activeSessions}</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Wait Time:</span>
          <span className={`font-semibold ${
            agent.waitTime > 60 ? 'text-yellow-600' : 'text-gray-900'
          }`}>
            {formatWaitTime(agent.waitTime)}
          </span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Productivity:</span>
          <span className="font-semibold text-gray-900">{agent.productivity.toFixed(0)}%</span>
        </div>
        
        <div className="flex justify-between items-center">
          <span className="text-gray-600">Last Activity:</span>
          <span className="text-xs text-gray-500">{agent.lastActivity}</span>
        </div>
      </div>
      
      {/* Productivity bar */}
      <div className="mt-3">
        <div className="flex justify-between text-xs text-gray-600 mb-1">
          <span>Productivity</span>
          <span>{agent.productivity.toFixed(0)}%</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className={`h-2 rounded-full transition-all duration-300 ${
              agent.productivity >= 80 ? 'bg-green-500' :
              agent.productivity >= 60 ? 'bg-yellow-500' :
              'bg-red-500'
            }`}
            style={{ width: `${agent.productivity}%` }}
          />
        </div>
      </div>
      
      {/* Active tasks */}
      {agent.tasks.length > 0 && (
        <div className="mt-3 pt-3 border-t border-gray-100">
          <p className="text-xs text-gray-600 mb-1">Active Tasks:</p>
          <div className="space-y-1">
            {agent.tasks.slice(0, 2).map((task, index) => (
              <div key={index} className="text-xs text-gray-700 bg-gray-50 px-2 py-1 rounded">
                {task}
              </div>
            ))}
            {agent.tasks.length > 2 && (
              <div className="text-xs text-gray-500">
                +{agent.tasks.length - 2} more tasks
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default AgentCard;