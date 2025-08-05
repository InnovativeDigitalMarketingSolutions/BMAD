"""
Enhanced MCP Performance Tests

Test performance van enhanced MCP integration en tracing.
"""

import pytest
import asyncio
import time
import os
import sys
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any, Optional

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../..")))

from bmad.core.mcp import MCPClient, MCPContext, FrameworkMCPIntegration
from bmad.agents.Agent import (
    BackendDeveloper, FrontendDeveloper, FullstackDeveloper, MobileDeveloper,
    AiDeveloper, Architect, UXUIDesigner, AccessibilityAgent, TestEngineer,
    QualityGuardian, ProductOwner, Scrummaster, ReleaseManager, DocumentationAgent,
    FeedbackAgent, DevOpsInfra, DataEngineer, SecurityDeveloper, StrategiePartner,
    Retrospective, RnD, Orchestrator, WorkflowAutomator
)

class TestEnhancedMCPPerformance:
    """Test performance van enhanced MCP integration."""
    
    @pytest.fixture
    def performance_agents(self):
        """Initialize agents voor performance testing."""
        return {
            'backend': BackendDeveloper(),
            'frontend': FrontendDeveloper(),
            'architect': Architect(),
            'test': TestEngineer(),
            'devops': DevOpsInfra()
        }
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_initialization_performance(self, performance_agents):
        """Test performance van enhanced MCP initialization."""
        results = {}
        
        for agent_name, agent in performance_agents.items():
            # Measure initialization time
            start_time = time.time()
            await agent.initialize_enhanced_mcp()
            end_time = time.time()
            
            duration = end_time - start_time
            results[agent_name] = duration
            
            # Should initialize within 2 seconds
            assert duration < 2.0, f"{agent_name}: Initialization too slow ({duration:.2f}s)"
            print(f"✅ {agent_name}: Enhanced MCP initialization {duration:.3f}s")
        
        # Calculate average
        avg_duration = sum(results.values()) / len(results)
        print(f"📊 Average initialization time: {avg_duration:.3f}s")
        
        # Average should be reasonable
        assert avg_duration < 1.0, f"Average initialization time too high: {avg_duration:.3f}s"
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_tool_performance(self, performance_agents):
        """Test performance van enhanced MCP tool usage."""
        results = {}
        
        for agent_name, agent in performance_agents.items():
            # Initialize enhanced MCP
            await agent.initialize_enhanced_mcp()
            
            if hasattr(agent, 'use_enhanced_mcp_tool'):
                # Measure tool usage performance
                start_time = time.time()
                
                # Test multiple tool calls
                for i in range(5):
                    await agent.use_enhanced_mcp_tool('performance_test', {
                        'iteration': i,
                        'agent': agent_name
                    })
                
                end_time = time.time()
                duration = end_time - start_time
                results[agent_name] = duration
                
                # Should complete 5 calls within 3 seconds
                assert duration < 3.0, f"{agent_name}: Tool usage too slow ({duration:.2f}s)"
                print(f"✅ {agent_name}: 5 tool calls in {duration:.3f}s")
            else:
                print(f"⚠️ {agent_name}: No enhanced MCP tools available")
        
        if results:
            avg_duration = sum(results.values()) / len(results)
            print(f"📊 Average tool usage time: {avg_duration:.3f}s")
    
    @pytest.mark.asyncio
    async def test_tracing_performance_impact(self, performance_agents):
        """Test performance impact van tracing."""
        results = {}
        
        for agent_name, agent in performance_agents.items():
            # Initialize enhanced MCP and tracing
            await agent.initialize_enhanced_mcp()
            await agent.initialize_tracing()
            
            if hasattr(agent, 'trace_agent_operation'):
                # Measure performance with tracing
                start_time = time.time()
                
                # Test multiple tracing operations
                for i in range(10):
                    await agent.trace_agent_operation({
                        'type': 'performance_test',
                        'agent_name': agent_name,
                        'iteration': i,
                        'performance_metrics': {'duration': 0.1}
                    })
                
                end_time = time.time()
                duration = end_time - start_time
                results[agent_name] = duration
                
                # Tracing should not add significant overhead (< 1 second for 10 operations)
                assert duration < 1.0, f"{agent_name}: Tracing overhead too high ({duration:.2f}s)"
                print(f"✅ {agent_name}: 10 tracing operations in {duration:.3f}s")
            else:
                print(f"⚠️ {agent_name}: No tracing methods available")
        
        if results:
            avg_duration = sum(results.values()) / len(results)
            print(f"📊 Average tracing time: {avg_duration:.3f}s")
    
    @pytest.mark.asyncio
    async def test_inter_agent_communication_performance(self, performance_agents):
        """Test performance van inter-agent communication."""
        # Test communication tussen pairs
        test_pairs = [
            ('backend', 'frontend'),
            ('architect', 'devops'),
            ('test', 'backend')
        ]
        
        results = {}
        
        for agent1_name, agent2_name in test_pairs:
            agent1 = performance_agents[agent1_name]
            agent2 = performance_agents[agent2_name]
            
            # Initialize both agents
            await agent1.initialize_enhanced_mcp()
            await agent2.initialize_enhanced_mcp()
            
            if hasattr(agent1, 'communicate_with_agent'):
                # Measure communication performance
                start_time = time.time()
                
                # Test multiple communications
                for i in range(3):
                    await agent1.communicate_with_agent(agent2_name, {
                        'message': f'test_communication_{i}',
                        'data': {'test': True, 'iteration': i}
                    })
                
                end_time = time.time()
                duration = end_time - start_time
                pair_name = f"{agent1_name}↔{agent2_name}"
                results[pair_name] = duration
                
                # Communication should be fast (< 2 seconds for 3 communications)
                assert duration < 2.0, f"{pair_name}: Communication too slow ({duration:.2f}s)"
                print(f"✅ {pair_name}: 3 communications in {duration:.3f}s")
            else:
                print(f"⚠️ {agent1_name}: No communication method available")
        
        if results:
            avg_duration = sum(results.values()) / len(results)
            print(f"📊 Average communication time: {avg_duration:.3f}s")
    
    @pytest.mark.asyncio
    async def test_memory_usage_performance(self, performance_agents):
        """Test memory usage van enhanced MCP integration."""
        import psutil
        import gc
        
        results = {}
        
        for agent_name, agent in performance_agents.items():
            # Get initial memory usage
            process = psutil.Process()
            initial_memory = process.memory_info().rss / 1024 / 1024  # MB
            
            # Initialize enhanced MCP
            await agent.initialize_enhanced_mcp()
            await agent.initialize_tracing()
            
            # Perform some operations
            if hasattr(agent, 'use_enhanced_mcp_tool'):
                for i in range(10):
                    await agent.use_enhanced_mcp_tool('memory_test', {
                        'iteration': i,
                        'agent': agent_name
                    })
            
            # Get final memory usage
            final_memory = process.memory_info().rss / 1024 / 1024  # MB
            memory_increase = final_memory - initial_memory
            
            results[agent_name] = memory_increase
            
            # Memory increase should be reasonable (< 50 MB)
            assert memory_increase < 50.0, f"{agent_name}: Memory usage too high (+{memory_increase:.1f}MB)"
            print(f"✅ {agent_name}: Memory increase {memory_increase:.1f}MB")
            
            # Clean up
            del agent
            gc.collect()
        
        if results:
            avg_memory_increase = sum(results.values()) / len(results)
            print(f"📊 Average memory increase: {avg_memory_increase:.1f}MB")
    
    @pytest.mark.asyncio
    async def test_concurrent_agent_performance(self, performance_agents):
        """Test performance van concurrent agent operations."""
        import asyncio
        
        async def agent_operation(agent_name, agent):
            """Perform concurrent operations on agent."""
            await agent.initialize_enhanced_mcp()
            
            if hasattr(agent, 'use_enhanced_mcp_tool'):
                for i in range(5):
                    await agent.use_enhanced_mcp_tool('concurrent_test', {
                        'agent': agent_name,
                        'iteration': i
                    })
                return f"{agent_name}: Completed"
            return f"{agent_name}: No tools available"
        
        # Run all agents concurrently
        start_time = time.time()
        
        tasks = [
            agent_operation(agent_name, agent) 
            for agent_name, agent in performance_agents.items()
        ]
        
        results = await asyncio.gather(*tasks)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Concurrent operations should complete within reasonable time
        assert duration < 10.0, f"Concurrent operations too slow ({duration:.2f}s)"
        
        print(f"✅ Concurrent operations completed in {duration:.3f}s")
        for result in results:
            print(f"  - {result}")
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_scalability(self, performance_agents):
        """Test scalability van enhanced MCP integration."""
        # Test with increasing number of operations
        operation_counts = [1, 5, 10, 20]
        results = {}
        
        for agent_name, agent in performance_agents.items():
            await agent.initialize_enhanced_mcp()
            
            if hasattr(agent, 'use_enhanced_mcp_tool'):
                agent_results = {}
                
                for count in operation_counts:
                    start_time = time.time()
                    
                    for i in range(count):
                        await agent.use_enhanced_mcp_tool('scalability_test', {
                            'operation': i,
                            'total': count
                        })
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    agent_results[count] = duration
                    
                    # Performance should scale reasonably
                    expected_max_time = count * 0.5  # 0.5 seconds per operation
                    assert duration < expected_max_time, f"{agent_name}: {count} operations too slow ({duration:.2f}s > {expected_max_time:.2f}s)"
                
                results[agent_name] = agent_results
                print(f"✅ {agent_name}: Scalability test passed")
            else:
                print(f"⚠️ {agent_name}: No enhanced MCP tools for scalability test")
        
        # Print scalability results
        for agent_name, agent_results in results.items():
            print(f"\n📊 {agent_name} Scalability Results:")
            for count, duration in agent_results.items():
                ops_per_sec = count / duration
                print(f"  {count:2d} operations: {duration:.3f}s ({ops_per_sec:.1f} ops/sec)")

class TestEnhancedMCPPerformanceBenchmarks:
    """Performance benchmarks voor enhanced MCP."""
    
    @pytest.mark.asyncio
    async def test_enhanced_mcp_benchmark_suite(self):
        """Complete benchmark suite voor enhanced MCP."""
        # Initialize test agents
        agents = {
            'backend': BackendDeveloper(),
            'frontend': FrontendDeveloper(),
            'architect': Architect()
        }
        
        benchmark_results = {}
        
        for agent_name, agent in agents.items():
            print(f"\n🏃 Running benchmarks for {agent_name}...")
            
            # Benchmark 1: Initialization
            start_time = time.time()
            await agent.initialize_enhanced_mcp()
            init_time = time.time() - start_time
            
            # Benchmark 2: Tool operations
            if hasattr(agent, 'use_enhanced_mcp_tool'):
                start_time = time.time()
                for i in range(10):
                    await agent.use_enhanced_mcp_tool('benchmark_test', {'iteration': i})
                tool_time = time.time() - start_time
            else:
                tool_time = None
            
            # Benchmark 3: Tracing operations
            await agent.initialize_tracing()
            if hasattr(agent, 'trace_agent_operation'):
                start_time = time.time()
                for i in range(10):
                    await agent.trace_agent_operation({
                        'type': 'benchmark_test',
                        'iteration': i,
                        'performance_metrics': {'duration': 0.1}
                    })
                trace_time = time.time() - start_time
            else:
                trace_time = None
            
            benchmark_results[agent_name] = {
                'initialization': init_time,
                'tool_operations': tool_time,
                'tracing_operations': trace_time
            }
            
            print(f"✅ {agent_name} benchmarks completed")
        
        # Print benchmark summary
        print(f"\n📊 Enhanced MCP Benchmark Summary:")
        print(f"{'Agent':<15} {'Init (s)':<10} {'Tools (s)':<10} {'Tracing (s)':<10}")
        print("-" * 50)
        
        for agent_name, results in benchmark_results.items():
            init_time = f"{results['initialization']:.3f}"
            tool_time = f"{results['tool_operations']:.3f}" if results['tool_operations'] else "N/A"
            trace_time = f"{results['tracing_operations']:.3f}" if results['tracing_operations'] else "N/A"
            
            print(f"{agent_name:<15} {init_time:<10} {tool_time:<10} {trace_time:<10}")
        
        # Performance assertions
        for agent_name, results in benchmark_results.items():
            assert results['initialization'] < 2.0, f"{agent_name}: Initialization benchmark failed"
            if results['tool_operations']:
                assert results['tool_operations'] < 5.0, f"{agent_name}: Tool operations benchmark failed"
            if results['tracing_operations']:
                assert results['tracing_operations'] < 2.0, f"{agent_name}: Tracing operations benchmark failed"

if __name__ == "__main__":
    # Run performance tests
    pytest.main([__file__, "-v", "--tb=short"]) 