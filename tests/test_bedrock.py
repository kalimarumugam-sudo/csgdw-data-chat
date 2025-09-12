import json
import time
import sys
import argparse
from typing import Dict, Any, List
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.aws_config import aws_config, bedrock_config, validate_config

# Load environment variables
load_dotenv()

async def test_bedrock():
    """Test AWS Bedrock connection and embedding generation"""
    print('🔍 Testing AWS Bedrock Connection...\n')
    
    print('📋 Configuration:')
    print(f'   Region: {aws_config.region}')
    print(f'   Profile: {aws_config.profile}')
    print(f'   Model: {bedrock_config.model_id}')
    print('')
    
    # Create Bedrock client
    session = aws_config.get_session()
    client = session.client('bedrock-runtime')
    
    # Test text for embedding generation
    test_text = "This is a test call from +1234567890 to +0987654321 with duration of 120 seconds."
    
    try:
        print('🔄 Connecting to Bedrock...')
        print(f'📝 Test text: "{test_text}"')
        print('')
        
        # Prepare request parameters
        body = json.dumps({
            "inputText": test_text
        })
        
        start_time = time.time()
        
        # Invoke the model
        response = client.invoke_model(
            modelId=bedrock_config.model_id,
            contentType='application/json',
            accept='application/json',
            body=body
        )
        
        end_time = time.time()
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        print('✅ Successfully connected to Bedrock!\n')
        
        print('📊 Model Response:')
        print(f'   Model: {bedrock_config.model_id}')
        print(f'   Response Time: {(end_time - start_time) * 1000:.0f}ms')
        print(f'   Embedding Dimensions: {len(response_body.get("embedding", []))}')
        
        if 'embedding' in response_body:
            embedding = response_body['embedding']
            first_five = [f"{v:.4f}" for v in embedding[:5]]
            print(f'   First 5 values: [{", ".join(first_five)}...]')
            print(f'   Embedding Range: [{min(embedding):.4f}, {max(embedding):.4f}]')
        
        print('\n🚦 Status Check:')
        print('   ✅ Bedrock is accessible')
        print('   ✅ Model is responding correctly')
        print('   ✅ Embeddings are being generated')
        
        print('\n✨ Bedrock is properly configured and ready for use with the application!')
        print('\nNext steps:')
        print('1. Ensure ChromaDB is running')
        print('2. Run the indexing script to process and index EDR data')
        
    except ClientError as error:
        error_code = error.response['Error']['Code']
        error_message = error.response['Error']['Message']
        
        print(f'\n❌ Error connecting to Bedrock: {error_message}')
        
        if error_code == 'ResourceNotFoundException':
            print('\n⚠️  Model not found. Please check:')
            print(f'   1. The model ID is correct: {bedrock_config.model_id}')
            print('   2. The model is available in your region')
            print('   3. You have access to the model')
        elif error_code == 'AccessDeniedException':
            print('\n⚠️  Access denied. Please check:')
            print('   1. Your AWS credentials have Bedrock permissions')
            print('   2. The IAM policy includes bedrock:InvokeModel')
            print('   3. You are using the correct AWS profile')
            print('   4. You have requested access to the model in Bedrock console')
        elif error_code == 'ValidationException':
            print('\n⚠️  Invalid request. Please check the model ID and request format')
        elif error_code == 'ThrottlingException':
            print('\n⚠️  Request throttled. You may be hitting rate limits')
        
        print('\n📚 For Bedrock setup:')
        print('   1. Go to AWS Bedrock console')
        print('   2. Request access to foundation models')
        print('   3. Enable "Amazon Titan Embeddings G1 - Text"')
        print('   4. Wait for access approval (usually instant)')
        
    except Exception as error:
        print(f'\n❌ Unexpected error: {str(error)}')

async def test_embedding_performance():
    """Test embedding generation performance with different text lengths"""
    print('\n\n📈 Testing Embedding Generation Performance...\n')
    
    # Create Bedrock client
    session = aws_config.get_session()
    client = session.client('bedrock-runtime')
    
    test_texts = [
        "Short call from +1111111111 to +2222222222",
        "Medium duration voice call from +3333333333 to +4444444444 lasting 5 minutes in downtown area",
        "Long international video conference call from +5555555555 to +6666666666 with duration of 45 minutes using 5G network in business district with high quality connection"
    ]
    
    try:
        print('🔄 Generating embeddings for different text lengths...\n')
        
        for text in test_texts:
            body = json.dumps({"inputText": text})
            
            start_time = time.time()
            
            client.invoke_model(
                modelId=bedrock_config.model_id,
                contentType='application/json',
                accept='application/json',
                body=body
            )
            
            end_time = time.time()
            
            print(f'📝 Text length: {len(text)} chars')
            print(f'   Time: {(end_time - start_time) * 1000:.0f}ms')
            print(f'   Sample: "{text[:50]}..."')
            print('')
        
        print('✅ Performance test complete!')
        
    except ClientError as error:
        print(f'❌ Performance test failed: {error.response["Error"]["Message"]}')
    except Exception as error:
        print(f'❌ Performance test failed: {str(error)}')

def test_bedrock_sync():
    """Synchronous version of test_bedrock for easier execution"""
    print('🔍 Testing AWS Bedrock Connection...\n')
    
    print('📋 Configuration:')
    print(f'   Region: {aws_config.region}')
    print(f'   Profile: {aws_config.profile}')
    print(f'   Model: {bedrock_config.model_id}')
    print('')
    
    # Create Bedrock client
    session = aws_config.get_session()
    client = session.client('bedrock-runtime')
    
    # Test text for embedding generation
    test_text = "This is a test call from +1234567890 to +0987654321 with duration of 120 seconds."
    
    try:
        print('🔄 Connecting to Bedrock...')
        print(f'📝 Test text: "{test_text}"')
        print('')
        
        # Prepare request parameters
        body = json.dumps({
            "inputText": test_text
        })
        
        start_time = time.time()
        
        # Invoke the model
        response = client.invoke_model(
            modelId=bedrock_config.model_id,
            contentType='application/json',
            accept='application/json',
            body=body
        )
        
        end_time = time.time()
        
        # Parse response
        response_body = json.loads(response['body'].read())
        
        print('✅ Successfully connected to Bedrock!\n')
        
        print('📊 Model Response:')
        print(f'   Model: {bedrock_config.model_id}')
        print(f'   Response Time: {(end_time - start_time) * 1000:.0f}ms')
        print(f'   Embedding Dimensions: {len(response_body.get("embedding", []))}')
        
        if 'embedding' in response_body:
            embedding = response_body['embedding']
            first_five = [f"{v:.4f}" for v in embedding[:5]]
            print(f'   First 5 values: [{", ".join(first_five)}...]')
            print(f'   Embedding Range: [{min(embedding):.4f}, {max(embedding):.4f}]')
        
        print('\n🚦 Status Check:')
        print('   ✅ Bedrock is accessible')
        print('   ✅ Model is responding correctly')
        print('   ✅ Embeddings are being generated')
        
        print('\n✨ Bedrock is properly configured and ready for use with the application!')
        print('\nNext steps:')
        print('1. Ensure ChromaDB is running')
        print('2. Run the indexing script to process and index EDR data')
        
        return True
        
    except ClientError as error:
        error_code = error.response['Error']['Code']
        error_message = error.response['Error']['Message']
        
        print(f'\n❌ Error connecting to Bedrock: {error_message}')
        
        if error_code == 'ResourceNotFoundException':
            print('\n⚠️  Model not found. Please check:')
            print(f'   1. The model ID is correct: {bedrock_config.model_id}')
            print('   2. The model is available in your region')
            print('   3. You have access to the model')
        elif error_code == 'AccessDeniedException':
            print('\n⚠️  Access denied. Please check:')
            print('   1. Your AWS credentials have Bedrock permissions')
            print('   2. The IAM policy includes bedrock:InvokeModel')
            print('   3. You are using the correct AWS profile')
            print('   4. You have requested access to the model in Bedrock console')
        elif error_code == 'ValidationException':
            print('\n⚠️  Invalid request. Please check the model ID and request format')
        elif error_code == 'ThrottlingException':
            print('\n⚠️  Request throttled. You may be hitting rate limits')
        
        print('\n📚 For Bedrock setup:')
        print('   1. Go to AWS Bedrock console')
        print('   2. Request access to foundation models')
        print('   3. Enable "Amazon Titan Embeddings G1 - Text"')
        print('   4. Wait for access approval (usually instant)')
        
        return False
        
    except Exception as error:
        print(f'\n❌ Unexpected error: {str(error)}')
        return False

def test_embedding_performance_sync():
    """Synchronous version of test_embedding_performance"""
    print('\n\n📈 Testing Embedding Generation Performance...\n')
    
    # Create Bedrock client
    session = aws_config.get_session()
    client = session.client('bedrock-runtime')
    
    test_texts = [
        "Short call from +1111111111 to +2222222222",
        "Medium duration voice call from +3333333333 to +4444444444 lasting 5 minutes in downtown area",
        "Long international video conference call from +5555555555 to +6666666666 with duration of 45 minutes using 5G network in business district with high quality connection"
    ]
    
    try:
        print('🔄 Generating embeddings for different text lengths...\n')
        
        for text in test_texts:
            body = json.dumps({"inputText": text})
            
            start_time = time.time()
            
            client.invoke_model(
                modelId=bedrock_config.model_id,
                contentType='application/json',
                accept='application/json',
                body=body
            )
            
            end_time = time.time()
            
            print(f'📝 Text length: {len(text)} chars')
            print(f'   Time: {(end_time - start_time) * 1000:.0f}ms')
            print(f'   Sample: "{text[:50]}..."')
            print('')
        
        print('✅ Performance test complete!')
        
    except ClientError as error:
        print(f'❌ Performance test failed: {error.response["Error"]["Message"]}')
    except Exception as error:
        print(f'❌ Performance test failed: {str(error)}')

def main():
    """Main function to run the tests"""
    parser = argparse.ArgumentParser(description='Test AWS Bedrock connection and performance')
    parser.add_argument('--perf', action='store_true', help='Run performance tests')
    args = parser.parse_args()
    
    try:
        # Validate configuration
        validate_config()
        
        # Run basic test
        success = test_bedrock_sync()
        
        if success and args.perf:
            test_embedding_performance_sync()
        elif success:
            print('\n💡 Tip: Run with --perf flag to test embedding performance')
            print('   python test_bedrock.py --perf')
            
    except Exception as error:
        print(f'❌ Test failed: {str(error)}')
        sys.exit(1)

if __name__ == "__main__":
    main()
